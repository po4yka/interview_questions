---
id: kotlin-207
title: "Inline функции / Inline functions"
aliases: [Inline функции, Inline functions]
topic: kotlin
subtopics: [coroutines, inline-functions]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-channels-basics-types--kotlin--medium, q-coroutine-timeout-withtimeout--kotlin--medium, q-kotlin-sealed-when-exhaustive--kotlin--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [difficulty/medium]
---

# Вопрос (RU)
> Что такое inline функции в Kotlin и зачем они нужны?

---

# Question (EN)
> What are inline functions in Kotlin and why use them?

## Ответ (RU)

Inline функции — это специальный тип функций, для которых компилятор пытается встроить (подставить) код функции в место её вызова, особенно при работе с лямбда-аргументами, чтобы уменьшить накладные расходы и избежать лишних объектов. Это не жёсткая гарантия для всех вызовов: компилятор может решить не инлайнить слишком крупные или сложные функции.

### Как Работает

```kotlin
inline fun measureTime(block: () -> Unit) {
    val start = System.currentTimeMillis()
    block()
    val end = System.currentTimeMillis()
    println("Time: ${end - start}ms")
}

// Использование
measureTime {
    // Код операции
    performOperation()
}

// Примерно во что может быть преобразовано компилятором:
val start = System.currentTimeMillis()
performOperation()  // Код лямбды и вызова встроен напрямую
val end = System.currentTimeMillis()
println("Time: ${end - start}ms")
```

### Для Чего Нужны

#### 1. Уменьшение Накладных Расходов На Вызов Функций (особенно с лямбдами)

Inline функции уменьшают накладные расходы на вызов высокоуровневых функций с лямбдой, так как вместо создания отдельных объектов-лямбд и косвенных вызовов их код подставляется напрямую. При этом важно понимать, что JVM JIT может инлайнить и обычные функции, поэтому эффект зависит от конкретного сценария.

#### 2. Улучшение Производительности При Использовании Лямбда-выражений

Kotlin обычно представляет лямбда-выражения объектами, что ведёт к дополнительным аллокациям и нагрузке на GC. Inline функции позволяют избежать создания объектов для лямбд-параметров, которые могут быть встроены, и вместо этого подставляют их код в вызывающий контекст.

```kotlin
// Без inline - создаётся объект для лямбды
fun repeat(times: Int, action: () -> Unit) {
    for (i in 0 until times) {
        action()  // Вызов через объект лямбды
    }
}

// С inline - лямбда может быть встроена напрямую
inline fun repeat(times: Int, action: () -> Unit) {
    for (i in 0 until times) {
        action()  // Код лямбды подставляется при вызове
    }
}
```

#### 3. Возможность Использования Реифицированных Типовых Параметров

Только inline функции могут использовать `reified` типовые параметры, что позволяет проверять типы и обращаться к ним во время выполнения, как к обычным классам.

```kotlin
// Без reified - не сработает
fun <T> isInstanceOf(value: Any): Boolean {
    return value is T  // Ошибка компиляции: cannot check for erased type T
}

// С inline + reified - работает
inline fun <reified T> isInstanceOf(value: Any): Boolean {
    return value is T  // OK
}

// Использование
val result = isInstanceOf<String>("Hello")  // true
val result2 = isInstanceOf<Int>("Hello")    // false
```

### Пример С Реальным Использованием

```kotlin
// Упрощённый пример inline-версии filter
inline fun <T> List<T>.filter(predicate: (T) -> Boolean): List<T> {
    val result = ArrayList<T>()
    for (element in this) {
        if (predicate(element)) {  // Тело лямбды может быть встроено
            result.add(element)
        }
    }
    return result
}

// Использование
val numbers = listOf(1, 2, 3, 4, 5)
val even = numbers.filter { it % 2 == 0 }

// Примерно во что может быть преобразовано (упрощённо):
val result = ArrayList<Int>()
for (element in numbers) {
    if (element % 2 == 0) {  // Код из лямбды подставлен напрямую
        result.add(element)
    }
}
```

### Noinline И Crossinline

`noinline` — отключает подстановку для конкретного параметра-лямбды, позволяя, например, сохранять его в переменную или передавать дальше.

```kotlin
inline fun foo(inlined: () -> Unit, noinline notInlined: () -> Unit) {
    inlined()      // Может быть встроен
    notInlined()   // Не будет встроен, остаётся как обычная лямбда
}
```

`crossinline` — запрещает non-local return из лямбды (нельзя сделать `return` из внешней функции), что необходимо для безопасного использования лямбды в других контекстах (например, в другом потоке).

```kotlin
inline fun runInThread(crossinline block: () -> Unit) {
    Thread {
        block()  // crossinline запрещает return из block, который бы вернул из runInThread
    }.start()
}
```

Также важно учитывать, что чрезмерное использование `inline` может привести к росту размера bytecode и ухудшению кэш-производительности, поэтому применять его следует осознанно.

## Answer (EN)

Inline functions are functions for which the compiler attempts to substitute the function body directly at the call site (especially for lambda parameters), reducing higher-order call overhead and avoiding extra allocations. This is a compile-time request/hint; the compiler may choose not to inline overly large or complex code.

Benefits:
1. Reduce overhead in higher-order APIs: less indirection and potential call overhead at the bytecode level.
2. Avoid lambda object allocation: lambda arguments can be inlined instead of being compiled as allocated objects, reducing GC pressure.
3. Enable reified type parameters: `reified` type parameters are only allowed in inline functions, enabling type checks and access to `T::class` at runtime.

Example:
```kotlin
inline fun measureTime(block: () -> Unit) {
    val start = System.currentTimeMillis()
    block()
    val end = System.currentTimeMillis()
    println("Time: ${end - start}ms")
}

// At call site, the compiler may generate code equivalent to:
val start = System.currentTimeMillis()
performOperation()  // inlined lambda/body
val end = System.currentTimeMillis()
println("Time: ${end - start}ms")
```

Typical use cases:
- Higher-order functions with lambda parameters (e.g., filter/map-style utilities)
- Functions requiring reified generics
- Performance-sensitive call patterns where avoiding lambda allocations or delegation is beneficial

Modifiers:
- `noinline`: disables inlining for a specific lambda parameter so it can be stored or passed around as a value.
- `crossinline`: disallows non-local returns from the lambda, making it safe to invoke in different execution contexts (threads, other lambdas).

Note: Excessive use of `inline` can increase bytecode size and potentially hurt performance; it should be used where its benefits (mainly for higher-order functions) are clear.

---

## Дополнительные вопросы (RU)

- В чем ключевые отличия inline-функций от реализации в Java?
- Когда целесообразно использовать inline-функции на практике?
- Каковы распространенные подводные камни и ограничения `inline`?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [[c-kotlin]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-kotlin-sealed-when-exhaustive--kotlin--medium]]
- [[q-coroutine-timeout-withtimeout--kotlin--medium]]
- [[q-channels-basics-types--kotlin--medium]]

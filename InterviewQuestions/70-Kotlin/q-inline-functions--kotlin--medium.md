---
id: kotlin-207
title: "Inline Functions"
aliases: [Inline, Functions]
topic: kotlin
subtopics: [coroutines, sealed-classes, inline-functions]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-kotlin-sealed-when-exhaustive--kotlin--medium, q-coroutine-timeout-withtimeout--kotlin--medium, q-channels-basics-types--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags:
  - 
  - difficulty/medium
---
# Что такое inline функции?

# Question (EN)
> What are inline functions in Kotlin and why use them?

# Вопрос (RU)
> Что такое inline функции в Kotlin и зачем они нужны?

---

## Answer (EN)

Inline functions insert their code directly at the call site during compilation instead of creating a new call stack.

**Benefits:**
1. **Reduces overhead** - no function call stack, better performance
2. **Avoids lambda object allocation** - lambdas are inlined, reducing GC pressure
3. **Enables reified type parameters** - runtime type checking with `reified`

**Example:**
```kotlin
inline fun measureTime(block: () -> Unit) {
    val start = System.currentTimeMillis()
    block()
    val end = System.currentTimeMillis()
    println("Time: ${end - start}ms")
}

// After compilation, becomes:
val start = System.currentTimeMillis()
performOperation()  // code inlined directly!
val end = System.currentTimeMillis()
println("Time: ${end - start}ms")
```

**Use cases:** Higher-order functions with lambda parameters (filter, map), reified generics, performance-critical code.

**Modifiers:** `noinline` (disables inlining for specific parameter), `crossinline` (prevents non-local returns).

---

## Ответ (RU)

Inline функции — это специальный тип функций, при компиляции которых код функции встраивается в место её вызова вместо создания нового стека вызовов.

### Как работает

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

// После компиляции превращается в:
val start = System.currentTimeMillis()
performOperation()  // Код встроен напрямую!
val end = System.currentTimeMillis()
println("Time: ${end - start}ms")
```

### Для чего нужны

#### 1. Уменьшение накладных расходов на вызов функций

Поскольку не происходит дополнительных вызовов функций и не создаётся новый стек, использование inline функций может значительно улучшить производительность.

#### 2. Улучшение производительности при использовании лямбда-выражений

Kotlin использует объекты для представления лямбда-выражений, что может привести к дополнительной нагрузке на сборщик мусора и память. Inline функции позволяют избежать этого.

```kotlin
// Без inline - создаётся объект для лямбды
fun repeat(times: Int, action: () -> Unit) {
    for (i in 0 until times) {
        action()  // Вызов через объект
    }
}

// С inline - лямбда встраивается напрямую
inline fun repeat(times: Int, action: () -> Unit) {
    for (i in 0 until times) {
        action()  // Код лямбды встроен
    }
}
```

#### 3. Возможность использования реифицированных типовых параметров

Только inline функции могут использовать `reified` типовые параметры, что позволяет работать с типами как с обычными классами.

```kotlin
// Без reified - не сработает
fun <T> isInstanceOf(value: Any): Boolean {
    return value is T  // Ошибка компиляции!
}

// С inline + reified - работает!
inline fun <reified T> isInstanceOf(value: Any): Boolean {
    return value is T  // OK!
}

// Использование
val result = isInstanceOf<String>("Hello")  // true
val result2 = isInstanceOf<Int>("Hello")    // false
```

### Пример с реальным использованием

```kotlin
// Стандартная inline функция из Kotlin
inline fun <T> List<T>.filter(predicate: (T) -> Boolean): List<T> {
    val result = ArrayList<T>()
    for (element in this) {
        if (predicate(element)) {  // Встраивается напрямую
            result.add(element)
        }
    }
    return result
}

// Использование
val numbers = listOf(1, 2, 3, 4, 5)
val even = numbers.filter { it % 2 == 0 }

// Компилируется примерно в:
val result = ArrayList<Int>()
for (element in numbers) {
    if (element % 2 == 0) {  // Лямбда встроена!
        result.add(element)
    }
}
```

### noinline и crossinline

**noinline** - отключает inlining для конкретного параметра:

```kotlin
inline fun foo(inlined: () -> Unit, noinline notInlined: () -> Unit) {
    inlined()      // Встроится
    notInlined()   // Не встроится
}
```

**crossinline** - запрещает non-local returns в лямбде:

```kotlin
inline fun runInThread(crossinline block: () -> Unit) {
    Thread {
        block()  // crossinline запрещает return из block
    }.start()
}
```

## Related Questions

- [[q-kotlin-sealed-when-exhaustive--kotlin--medium]]
- [[q-coroutine-timeout-withtimeout--kotlin--medium]]
- [[q-channels-basics-types--kotlin--medium]]

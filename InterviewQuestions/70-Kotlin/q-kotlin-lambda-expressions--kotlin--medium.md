---
id: kotlin-007
title: "Lambda Expressions in Kotlin / Лямбда-выражения в Kotlin"
aliases: ["Lambda Expressions in Kotlin", "Лямбда-выражения в Kotlin"]

# Classification
topic: kotlin
subtopics: [higher-order-functions, lambda-expressions]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: "https://github.com/Kirchhoff-/Android-Interview-Questions"
source_note: Kirchhoff Android Interview Questions repository - adapted from functional interfaces content

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-kotlin, c-kotlin-features, q-kotlin-higher-order-functions--kotlin--medium]

# Timestamps
created: 2025-10-05
updated: 2025-11-09

tags: [difficulty/medium, functional-programming, kotlin, lambda-expressions, sam-conversion]
---
# Вопрос (RU)
> Что такое лямбда-выражения в Kotlin и как они работают?

---

# Question (EN)
> What are lambda expressions in Kotlin and how do they work?

## Ответ (RU)

Лямбда-выражения (или лямбда-функции) — это анонимные функции, которые можно использовать для создания функциональных литералов. Они предоставляют лаконичный способ представления блока кода, который можно передавать и выполнять позже.

См. также: [[c-kotlin]], [[c-kotlin-features]].

### Базовый Синтаксис

```kotlin
// Синтаксис лямбды: { параметры -> тело }
val sum = { a: Int, b: Int -> a + b }
println(sum(3, 5))  // Вывод: 8

// Лямбда без параметров
val greet = { println("Hello!") }
greet()  // Вывод: Hello!

// Лямбда с одним параметром (можно использовать 'it')
val double = { x: Int -> x * 2 }
val doubleSimplified = { it: Int -> it * 2 }
```

### Вывод Типов

Kotlin часто может вывести типы параметров лямбды:

```kotlin
// Тип явно указан
val numbers = listOf(1, 2, 3, 4, 5)
val doubled = numbers.map { x: Int -> x * 2 }

// Тип выведен из контекста
val doubledInferred = numbers.map { x -> x * 2 }

// Использование 'it' для одного параметра
val doubledIt = numbers.map { it * 2 }
```

### Лямбда Как Параметр Функции

Лямбды обычно передаются как аргументы функциям высшего порядка:

```kotlin
// Функция, принимающая лямбду
fun performOperation(a: Int, b: Int, operation: (Int, Int) -> Int): Int {
    return operation(a, b)
}

// Использование лямбды
val result1 = performOperation(5, 3) { x, y -> x + y }  // 8
val result2 = performOperation(5, 3) { x, y -> x * y }  // 15

// Больше примеров
fun processString(str: String, processor: (String) -> String): String {
    return processor(str)
}

val uppercase = processString("hello") { it.uppercase() }  // "HELLO"
val reversed = processString("hello") { it.reversed() }   // "olleh"
```

### SAM-преобразование (Single Abstract Method)

Для функциональных интерфейсов (интерфейсов с одним абстрактным методом) можно использовать SAM-преобразования, которые помогают сделать код более лаконичным, используя лямбда-выражения. В Kotlin это применимо к:
- Java-функциональным интерфейсам;
- Kotlin-интерфейсам, объявленным как `fun interface`.

Вместо создания класса, который реализует функциональный интерфейс вручную, можно использовать лямбда-выражение:

```kotlin
fun interface IntPredicate {
    fun accept(i: Int): Boolean
}

// Без SAM-преобразования - многословно
val isEven1 = object : IntPredicate {
    override fun accept(i: Int): Boolean {
        return i % 2 == 0
    }
}

// С SAM-преобразованием - лаконичная лямбда
val isEven2 = IntPredicate { it % 2 == 0 }

// Использование
println("Is 7 even? - ${isEven2.accept(7)}")  // false
println("Is 8 even? - ${isEven2.accept(8)}")  // true
```

### Синтаксис Замыкающей Лямбды

Если лямбда является последним параметром функции, её можно вынести за скобки:

```kotlin
// Последний параметр - лямбда - можно вынести за скобки
val numbers = listOf(1, 2, 3, 4, 5)
val evens = numbers.filter { it % 2 == 0 }

// Если лямбда - единственный параметр, скобки можно опустить
repeat(3) {
    println("Hello")
}

// Несколько параметров с замыкающей лямбдой
fun calculate(x: Int, y: Int, operation: (Int, Int) -> Int): Int {
    return operation(x, y)
}

val sum = calculate(5, 3) { a, b -> a + b }
```

### Лямбда С Получателем

Лямбды можно определять с типом-получателем, что позволяет вызывать методы объекта без квалификации:

```kotlin
// Лямбда с получателем
fun buildString(builderAction: StringBuilder.() -> Unit): String {
    val sb = StringBuilder()
    sb.builderAction()  // Вызывает лямбду с sb как получателем
    return sb.toString()
}

val result = buildString {
    append("Hello")  // 'this' - это StringBuilder
    append(" ")
    append("World")
}
println(result)  // "Hello World"
```

### Захват Переменных (Замыкания)

Лямбды могут обращаться к переменным из окружающей области видимости и изменять их:

```kotlin
var sum = 0
val numbers = listOf(1, 2, 3, 4, 5)
numbers.forEach {
    sum += it  // Захватывает и изменяет 'sum' из внешней области видимости
}
println(sum)  // 15

// Захват неизменяемых значений
val prefix = "Number: "
numbers.map { "$prefix$it" }  // [Number: 1, Number: 2, ...]
```

### Возврат Из Лямбды

Поведение `return` в лямбдах зависит от контекста вызова:

```kotlin
// Нелокальный возврат возможен только при вызове из inline-функции
fun processNumbers(numbers: List<Int>): Int {
    numbers.forEach {
        if (it < 0) return -1  // Нелокальный return: возвращает из processNumbers, т.к. forEach - inline
    }
    return 0
}

// Метка для возврата только из лямбды (локальный возврат)
fun processNumbersLabeled(numbers: List<Int>): Int {
    numbers.forEach {
        if (it < 0) return@forEach  // Возвращает управление только из лямбды, цикл продолжается
    }
    return 0
}

// Пользовательская метка
fun processNumbersCustomLabel(numbers: List<Int>): Int {
    numbers.forEach loop@{
        if (it < 0) return@loop  // Локальный возврат из лямбды с пользовательской меткой
    }
    return 0
}
```

Коротко: нелокальные `return` возможны только в лямбдах, передаваемых в inline-функции (и не помеченных `crossinline`/`noinline`). В противном случае `return` (или `return@label`) относится только к самой лямбде.

### Общие Случаи Использования

#### 1. Операции С Коллекциями

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val doubled = numbers.map { it * 2 }           // [2, 4, 6, 8, 10]
val evens = numbers.filter { it % 2 == 0 }     // [2, 4]
val sum = numbers.reduce { acc, n -> acc + n } // 15
```

#### 2. Обработчики Событий

```kotlin
button.setOnClickListener { view ->
    Toast.makeText(context, "Clicked!", Toast.LENGTH_SHORT).show()
}
```

#### 3. Асинхронные Операции

```kotlin
GlobalScope.launch {
    val result = async { heavyComputation() }
    updateUI(result.await())
}
```

#### 4. Построение DSL

```kotlin
html {
    body {
        div {
            +"Hello, World!"
        }
    }
}
```

### Лямбда Vs Анонимная Функция

```kotlin
// Лямбда
val lambda = { x: Int -> x * 2 }

// Анонимная функция (похожа, но иное поведение return)
val anonymousFunc = fun(x: Int): Int {
    return x * 2
}

// Анонимная функция позволяет явно указать тип возврата
val typedFunc = fun(x: Int): String = x.toString()
```

**Краткое содержание**: Лямбда-выражения — это анонимные функции с лаконичным синтаксисом `{ параметры -> тело }`. Они поддерживают вывод типов, могут захватывать переменные из окружающей области видимости (замыкания), работают с SAM-преобразованием для функциональных интерфейсов (`fun interface` и Java SAM-типы) и поддерживают синтаксис замыкающей лямбды. Часто используются в операциях с коллекциями, обработчиках событий и паттернах функционального программирования.

---

## Answer (EN)

Lambda expressions (or lambda functions) are anonymous functions that can be used to create function literals. They provide a concise way to represent a block of code that can be passed around and executed later.

See also: [[c-kotlin]], [[c-kotlin-features]].

### Basic Syntax

```kotlin
// Lambda syntax: { parameters -> body }
val sum = { a: Int, b: Int -> a + b }
println(sum(3, 5))  // Output: 8

// Lambda with no parameters
val greet = { println("Hello!") }
greet()  // Output: Hello!

// Lambda with single parameter (can use 'it')
val double = { x: Int -> x * 2 }
val doubleSimplified = { it: Int -> it * 2 }
```

### Type Inference

Kotlin can often infer the types of lambda parameters:

```kotlin
// Type explicitly specified
val numbers = listOf(1, 2, 3, 4, 5)
val doubled = numbers.map { x: Int -> x * 2 }

// Type inferred from context
val doubledInferred = numbers.map { x -> x * 2 }

// Using 'it' for single parameter
val doubledIt = numbers.map { it * 2 }
```

### Lambda as Function Parameter

Lambdas are commonly passed as arguments to higher-order functions:

```kotlin
// Function that accepts a lambda
fun performOperation(a: Int, b: Int, operation: (Int, Int) -> Int): Int {
    return operation(a, b)
}

// Using lambda
val result1 = performOperation(5, 3) { x, y -> x + y }  // 8
val result2 = performOperation(5, 3) { x, y -> x * y }  // 15

// More examples
fun processString(str: String, processor: (String) -> String): String {
    return processor(str)
}

val uppercase = processString("hello") { it.uppercase() }  // "HELLO"
val reversed = processString("hello") { it.reversed() }   // "olleh"
```

### SAM Conversion (Single Abstract Method)

For functional interfaces (interfaces with only one abstract method), you can use SAM conversions that help make code more concise by using lambda expressions. In Kotlin this applies to:
- Java functional interfaces;
- Kotlin interfaces declared as `fun interface`.

Instead of creating a class that implements a functional interface manually, you can use a lambda expression:

```kotlin
fun interface IntPredicate {
    fun accept(i: Int): Boolean
}

// Without SAM conversion - verbose
val isEven1 = object : IntPredicate {
    override fun accept(i: Int): Boolean {
        return i % 2 == 0
    }
}

// With SAM conversion - concise lambda
val isEven2 = IntPredicate { it % 2 == 0 }

// Using it
println("Is 7 even? - ${isEven2.accept(7)}")  // false
println("Is 8 even? - ${isEven2.accept(8)}")  // true
```

### Trailing Lambda Syntax

If a lambda is the last parameter of a function, it can be placed outside the parentheses:

```kotlin
// Last parameter is lambda - can be outside parentheses
val numbers = listOf(1, 2, 3, 4, 5)
val evens = numbers.filter { it % 2 == 0 }

// If lambda is the only parameter, parentheses can be omitted
repeat(3) {
    println("Hello")
}

// Multiple parameters with trailing lambda
fun calculate(x: Int, y: Int, operation: (Int, Int) -> Int): Int {
    return operation(x, y)
}

val sum = calculate(5, 3) { a, b -> a + b }
```

### Lambda with Receiver

Lambdas can be defined with a receiver type, allowing you to call methods on an object without qualifying them:

```kotlin
// Lambda with receiver
fun buildString(builderAction: StringBuilder.() -> Unit): String {
    val sb = StringBuilder()
    sb.builderAction()  // Calls lambda with sb as receiver
    return sb.toString()
}

val result = buildString {
    append("Hello")  // 'this' is StringBuilder
    append(" ")
    append("World")
}
println(result)  // "Hello World"
```

### Capturing Variables (Closures)

Lambdas can access and modify variables from the enclosing scope:

```kotlin
var sum = 0
val numbers = listOf(1, 2, 3, 4, 5)
numbers.forEach {
    sum += it  // Captures and modifies 'sum' from outer scope
}
println(sum)  // 15

// Capturing immutable values
val prefix = "Number: "
numbers.map { "$prefix$it" }  // [Number: 1, Number: 2, ...]
```

### Returning from Lambda

The behavior of `return` inside lambdas depends on the call context:

```kotlin
// Non-local return is possible only when called from an inline function
fun processNumbers(numbers: List<Int>): Int {
    numbers.forEach {
        if (it < 0) return -1  // Non-local return: returns from processNumbers because forEach is inline
    }
    return 0
}

// Label to return from the lambda only (local return)
fun processNumbersLabeled(numbers: List<Int>): Int {
    numbers.forEach {
        if (it < 0) return@forEach  // Returns only from the lambda, continues forEach
    }
    return 0
}

// Custom label
fun processNumbersCustomLabel(numbers: List<Int>): Int {
    numbers.forEach loop@{
        if (it < 0) return@loop  // Local return from the lambda using custom label
    }
    return 0
}
```

In short: non-local `return` is only allowed from lambdas passed to inline functions (that are not marked `crossinline`/`noinline`). Otherwise, `return` (or `return@label`) applies only to the lambda itself.

### Common Use Cases

#### 1. Collection Operations

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val doubled = numbers.map { it * 2 }           // [2, 4, 6, 8, 10]
val evens = numbers.filter { it % 2 == 0 }     // [2, 4]
val sum = numbers.reduce { acc, n -> acc + n } // 15
```

#### 2. Event Handlers

```kotlin
button.setOnClickListener { view ->
    Toast.makeText(context, "Clicked!", Toast.LENGTH_SHORT).show()
}
```

#### 3. Asynchronous Operations

```kotlin
GlobalScope.launch {
    val result = async { heavyComputation() }
    updateUI(result.await())
}
```

#### 4. DSL Construction

```kotlin
html {
    body {
        div {
            +"Hello, World!"
        }
    }
}
```

### Lambda Vs Anonymous Function

```kotlin
// Lambda
val lambda = { x: Int -> x * 2 }

// Anonymous function (similar but different return behavior)
val anonymousFunc = fun(x: Int): Int {
    return x * 2
}

// Anonymous function allows explicit return type
val typedFunc = fun(x: Int): String = x.toString()
```

**English Summary**: Lambda expressions are anonymous functions with concise syntax `{ parameters -> body }`. They support type inference, can capture variables from enclosing scope (closures), work with SAM conversion for functional interfaces (`fun interface` and Java SAM types), and support trailing lambda syntax. Common in collection operations, event handlers, and functional programming patterns.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Lambdas - Kotlin Documentation](https://kotlinlang.org/docs/lambdas.html)
- [Functional (SAM) interfaces](https://kotlinlang.org/docs/fun-interfaces.html)
- [SAM Conversions in Kotlin](https://www.baeldung.com/kotlin/sam-conversions)
- [Everything about Functional interfaces in Kotlin](https://www.droidcon.com/2024/05/31/everything-you-want-to-know-about-functional-interfaces-in-kotlin/)

## Related Questions
- [[q-kotlin-higher-order-functions--kotlin--medium]]
- [[q-kotlin-inline-functions--kotlin--medium]]
- [[q-kotlin-scope-functions--kotlin--medium]]

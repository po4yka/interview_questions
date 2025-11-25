---
id: kotlin-005
title: "Higher-Order Functions in Kotlin / Функции высшего порядка в Kotlin"
aliases: ["Higher-Order Functions in Kotlin", "Функции высшего порядка в Kotlin"]

# Classification
topic: kotlin
subtopics: [functional-programming, higher-order-functions, inline-functions]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository - adapted from inline functions content

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-kotlin, q-kotlin-collections--kotlin--easy, q-kotlin-extensions--programming-languages--easy]

# Timestamps
created: 2025-10-05
updated: 2025-11-09

tags: [difficulty/medium, functional-programming, higher-order-functions, kotlin, lambda-expressions]
date created: Sunday, October 12th 2025, 12:27:46 pm
date modified: Tuesday, November 25th 2025, 8:53:50 pm
---

# Вопрос (RU)
> Что такое функции высшего порядка в Kotlin?

---

# Question (EN)
> What are higher-order functions in Kotlin?

## Ответ (RU)

**Функция высшего порядка** — это функция, которая принимает одну или несколько функций в качестве параметров или возвращает функцию в качестве результата (или и то, и другое). Это обеспечивает паттерны функционального программирования и делает код более переиспользуемым и выразительным.

См. также: [[c-kotlin]]

### Базовая Концепция

```kotlin
// Функция высшего порядка: принимает функцию как параметр
fun calculate(x: Int, y: Int, operation: (Int, Int) -> Int): Int {
    return operation(x, y)
}

// Использование функции высшего порядка
val sum = calculate(5, 3) { a, b -> a + b }        // 8
val product = calculate(5, 3) { a, b -> a * b }    // 15
val max = calculate(5, 3) { a, b -> if (a > b) a else b }  // 5
```

### Типы Функций

В Kotlin типы функций указываются с помощью синтаксиса: `(ТипыПараметров) -> ТипВозврата`

```kotlin
// Примеры типов функций
val noParams: () -> Unit = { println("Без параметров") }
val oneParam: (Int) -> Int = { it * 2 }
val twoParams: (Int, Int) -> Int = { a, b -> a + b }
val returnsString: (Int) -> String = { "Number: $it" }

// Nullable тип функции
val nullableFunc: ((Int) -> Int)? = null

// Тип функции с получателем
val withReceiver: String.() -> Int = { this.length }
```

### Общие Паттерны

#### 1. Функция Как Параметр

```kotlin
// Функция filter - принимает функцию-предикат
fun filter(numbers: List<Int>, predicate: (Int) -> Boolean): List<Int> {
    val result = mutableListOf<Int>()
    for (number in numbers) {
        if (predicate(number)) {
            result.add(number)
        }
    }
    return result
}

val numbers = listOf(1, 2, 3, 4, 5, 6)
val evens = filter(numbers) { it % 2 == 0 }  // [2, 4, 6]
val greaterThanThree = filter(numbers) { it > 3 }  // [4, 5, 6]
```

#### 2. Функция Как Возвращаемое Значение

```kotlin
// Возвращает функцию
fun multiplyBy(factor: Int): (Int) -> Int {
    return { number -> number * factor }
}

val double = multiplyBy(2)
val triple = multiplyBy(3)

println(double(5))  // 10
println(triple(5))  // 15

// Более сложный пример
fun getPriceCalculator(discount: Double): (Double) -> Double {
    return { price -> price * (1 - discount) }
}

val studentDiscount = getPriceCalculator(0.2)  // скидка 20%
val seniorDiscount = getPriceCalculator(0.3)   // скидка 30%

println(studentDiscount(100.0))  // 80.0
println(seniorDiscount(100.0))   // 70.0
```

#### 3. Несколько Функциональных Параметров

```kotlin
fun doubleAction(
    action1: () -> Unit,
    action2: () -> Unit
) {
    println("Starting actions...")
    action1()
    action2()
    println("Actions completed")
}

doubleAction(
    { println("First action") },
    { println("Second action") }
)
```

### Примеры Из Стандартной Библиотеки

Стандартная библиотека Kotlin активно использует функции высшего порядка:

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

// map: преобразует каждый элемент
val doubled = numbers.map { it * 2 }  // [2, 4, 6, 8, 10]

// filter: выбирает элементы, соответствующие предикату
val evens = numbers.filter { it % 2 == 0 }  // [2, 4]

// reduce: объединяет элементы в одно значение
val sum = numbers.reduce { acc, n -> acc + n }  // 15

// forEach: выполняет действие для каждого элемента
numbers.forEach { println(it) }

// any: проверяет, соответствует ли хотя бы один элемент предикату
val hasEvens = numbers.any { it % 2 == 0 }  // true

// all: проверяет, соответствуют ли все элементы предикату
val allPositive = numbers.all { it > 0 }  // true

// groupBy: группирует элементы по ключу
val grouped = numbers.groupBy { it % 2 }
// {1=[1, 3, 5], 0=[2, 4]}
```

### Соображения Производительности

Использование функций высшего порядка может создавать накладные расходы времени выполнения. Лямбды и ссылки на функции представляются объектами, и если они захватывают внешние переменные, создаются замыкания. Выделение памяти (для функциональных объектов и возможных замыканий) и виртуальные вызовы вносят дополнительный оверхед.

#### Ключевое Слово Inline

Чтобы уменьшить эти накладные расходы, вы можете пометить функции высшего порядка модификатором `inline`. Во многих случаях компилятор встраивает вызов функции и лямбд, переданных как параметры, непосредственно в место вызова, что позволяет избежать создания дополнительных объектов и косвенных вызовов.

```kotlin
// Без inline - обычно создаётся объект функции для лямбды
fun repeat(times: Int, action: () -> Unit) {
    for (i in 0 until times) {
        action()  // Вызов через функциональный объект
    }
}

// С inline - код (включая лямбду) может быть встроен
inline fun repeatInlined(times: Int, action: () -> Unit) {
    for (i in 0 until times) {
        action()  // Тело лямбды может быть встроено напрямую
    }
}
```

**Пример с inline:**

```kotlin
inline fun <T> lock(lock: Lock, body: () -> T): T {
    lock.lock()
    try {
        return body()
    } finally {
        lock.unlock()
    }
}

// Использование
lock(myLock) {
    // критическая секция
    performOperation()
}

// После компиляции (упрощённо) может быть преобразовано в:
myLock.lock()
try {
    performOperation()
} finally {
    myLock.unlock()
}
```

### Примеры Из Реальной Практики

#### 1. Управление Ресурсами

```kotlin
inline fun <T : Closeable, R> T.use(block: (T) -> R): R {
    var exception: Throwable? = null
    try {
        return block(this)
    } catch (e: Throwable) {
        exception = e
        throw e
    } finally {
        when {
            exception == null -> close()
            else -> try {
                close()
            } catch (closeException: Throwable) {
                exception.addSuppressed(closeException)
            }
        }
    }
}

// Использование
FileInputStream("file.txt").use { input ->
    // Чтение из файла
    // Автоматически закрывается по завершении
}
```

#### 2. Логика транзакций/повторов

```kotlin
fun <T> retry(
    times: Int = 3,
    delayMs: Long = 1000,
    operation: () -> T
): T {
    repeat(times - 1) { attempt ->
        try {
            return operation()
        } catch (e: Exception) {
            println("Attempt ${attempt + 1} failed: ${e.message}")
            Thread.sleep(delayMs)
        }
    }
    return operation()  // Последняя попытка без перехвата
}

// Использование
val result = retry(times = 3) {
    fetchDataFromAPI()
}
```

#### 3. Измерение Времени Выполнения

```kotlin
inline fun <T> measureTime(block: () -> T): Pair<T, Long> {
    val start = System.currentTimeMillis()
    val result = block()
    val duration = System.currentTimeMillis() - start
    return result to duration
}

// Использование
val (data, time) = measureTime {
    loadLargeDataset()
}
println("Loaded in ${time}ms")
```

#### 4. Построение DSL

```kotlin
class HTML {
    fun body(init: Body.() -> Unit): Body {
        val body = Body()
        body.init()
        return body
    }
}

class Body {
    fun div(init: Div.() -> Unit): Div {
        val div = Div()
        div.init()
        return div
    }
}

class Div {
    var text: String = ""
}

// Использование
fun html(init: HTML.() -> Unit): HTML {
    val html = HTML()
    html.init()
    return html
}

val page = html {
    body {
        div {
            text = "Hello, World!"
        }
    }
}
```

### Преимущества Функций Высшего Порядка

1. **Переиспользуемость кода** - Пишите универсальные алгоритмы, которые работают с разным поведением
2. **Абстракция** - Разделяйте "что делать" от "как делать"
3. **Композируемость** - Объединяйте маленькие функции в большие операции
4. **Читаемость** - Выражайте намерение ясно и лаконично
5. **Гибкость** - Изменяйте поведение без изменения структуры функции

**Краткое содержание**: Функции высшего порядка принимают функции как параметры или возвращают функции как результаты. Они обеспечивают паттерны функционального программирования, переиспользуемость кода и абстракцию. Стандартная библиотека Kotlin (map, filter, reduce) активно их использует. Ключевое слово `inline` помогает снизить накладные расходы, встраивая код лямбд и тела функции во время компиляции там, где это возможно.

---

## Answer (EN)

A **higher-order function** is a function that takes one or more functions as parameters or returns a function as a result (or both). This enables functional programming patterns and makes code more reusable and expressive.

See also: [[c-kotlin]]

### Basic Concept

```kotlin
// Higher-order function: takes a function as parameter
fun calculate(x: Int, y: Int, operation: (Int, Int) -> Int): Int {
    return operation(x, y)
}

// Using the higher-order function
val sum = calculate(5, 3) { a, b -> a + b }        // 8
val product = calculate(5, 3) { a, b -> a * b }    // 15
val max = calculate(5, 3) { a, b -> if (a > b) a else b }  // 5
```

### Function Types

In Kotlin, function types are specified using the syntax: `(ParameterTypes) -> ReturnType`.

```kotlin
// Function type examples
val noParams: () -> Unit = { println("No parameters") }
val oneParam: (Int) -> Int = { it * 2 }
val twoParams: (Int, Int) -> Int = { a, b -> a + b }
val returnsString: (Int) -> String = { "Number: $it" }

// Nullable function type
val nullableFunc: ((Int) -> Int)? = null

// Function type with receiver
val withReceiver: String.() -> Int = { this.length }
```

### Common Patterns

#### 1. Function as Parameter

```kotlin
// Filter function - takes predicate function
fun filter(numbers: List<Int>, predicate: (Int) -> Boolean): List<Int> {
    val result = mutableListOf<Int>()
    for (number in numbers) {
        if (predicate(number)) {
            result.add(number)
        }
    }
    return result
}

val numbers = listOf(1, 2, 3, 4, 5, 6)
val evens = filter(numbers) { it % 2 == 0 }  // [2, 4, 6]
val greaterThanThree = filter(numbers) { it > 3 }  // [4, 5, 6]
```

#### 2. Function as Return Value

```kotlin
// Returns a function
fun multiplyBy(factor: Int): (Int) -> Int {
    return { number -> number * factor }
}

val double = multiplyBy(2)
val triple = multiplyBy(3)

println(double(5))  // 10
println(triple(5))  // 15

// More complex example
fun getPriceCalculator(discount: Double): (Double) -> Double {
    return { price -> price * (1 - discount) }
}

val studentDiscount = getPriceCalculator(0.2)  // 20% off
val seniorDiscount = getPriceCalculator(0.3)   // 30% off

println(studentDiscount(100.0))  // 80.0
println(seniorDiscount(100.0))   // 70.0
```

#### 3. Multiple Function Parameters

```kotlin
fun doubleAction(
    action1: () -> Unit,
    action2: () -> Unit
) {
    println("Starting actions...")
    action1()
    action2()
    println("Actions completed")
}

doubleAction(
    { println("First action") },
    { println("Second action") }
)
```

### Standard Library Examples

Kotlin's standard library extensively uses higher-order functions:

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

// map: transforms each element
val doubled = numbers.map { it * 2 }  // [2, 4, 6, 8, 10]

// filter: selects elements matching predicate
val evens = numbers.filter { it % 2 == 0 }  // [2, 4]

// reduce: combines elements into single value
val sum = numbers.reduce { acc, n -> acc + n }  // 15

// forEach: performs action on each element
numbers.forEach { println(it) }

// any: checks if any element matches predicate
val hasEvens = numbers.any { it % 2 == 0 }  // true

// all: checks if all elements match predicate
val allPositive = numbers.all { it > 0 }  // true

// groupBy: groups elements by key selector
val grouped = numbers.groupBy { it % 2 }
// {1=[1, 3, 5], 0=[2, 4]}
```

### Performance Considerations

Using higher-order functions can introduce runtime overhead. Lambdas and function references are represented as objects, and when they capture external variables, closures are created. Memory allocations (for such function objects and closures) and virtual calls add overhead.

#### The Inline Keyword

To reduce this overhead, you can mark higher-order functions with the `inline` modifier. In many cases, the compiler will inline the function body and the lambdas passed as arguments at the call site, which can avoid extra allocations and indirection.

```kotlin
// Without inline - typically creates a function object for the lambda
fun repeat(times: Int, action: () -> Unit) {
    for (i in 0 until times) {
        action()  // Call through functional object
    }
}

// With inline - code (including lambda) can be inlined
inline fun repeatInlined(times: Int, action: () -> Unit) {
    for (i in 0 until times) {
        action()  // Lambda body may be inlined directly
    }
}
```

**Example with inline:**

```kotlin
inline fun <T> lock(lock: Lock, body: () -> T): T {
    lock.lock()
    try {
        return body()
    } finally {
        lock.unlock()
    }
}

// Usage
lock(myLock) {
    // critical section
    performOperation()
}

// After compilation, this can (simplified) become:
myLock.lock()
try {
    performOperation()
} finally {
    myLock.unlock()
}
```

### Real-World Examples

#### 1. Resource Management

```kotlin
inline fun <T : Closeable, R> T.use(block: (T) -> R): R {
    var exception: Throwable? = null
    try {
        return block(this)
    } catch (e: Throwable) {
        exception = e
        throw e
    } finally {
        when {
            exception == null -> close()
            else -> try {
                close()
            } catch (closeException: Throwable) {
                exception.addSuppressed(closeException)
            }
        }
    }
}

// Usage
FileInputStream("file.txt").use { input ->
    // Read from file
    // Automatically closed when done
}
```

#### 2. Transaction/Retry Logic

```kotlin
fun <T> retry(
    times: Int = 3,
    delayMs: Long = 1000,
    operation: () -> T
): T {
    repeat(times - 1) { attempt ->
        try {
            return operation()
        } catch (e: Exception) {
            println("Attempt ${attempt + 1} failed: ${e.message}")
            Thread.sleep(delayMs)
        }
    }
    return operation()  // Last attempt without catching
}

// Usage
val result = retry(times = 3) {
    fetchDataFromAPI()
}
```

#### 3. Measuring Execution Time

```kotlin
inline fun <T> measureTime(block: () -> T): Pair<T, Long> {
    val start = System.currentTimeMillis()
    val result = block()
    val duration = System.currentTimeMillis() - start
    return result to duration
}

// Usage
val (data, time) = measureTime {
    loadLargeDataset()
}
println("Loaded in ${time}ms")
```

#### 4. DSL Construction

```kotlin
class HTML {
    fun body(init: Body.() -> Unit): Body {
        val body = Body()
        body.init()
        return body
    }
}

class Body {
    fun div(init: Div.() -> Unit): Div {
        val div = Div()
        div.init()
        return div
    }
}

class Div {
    var text: String = ""
}

// Usage
fun html(init: HTML.() -> Unit): HTML {
    val html = HTML()
    html.init()
    return html
}

val page = html {
    body {
        div {
            text = "Hello, World!"
        }
    }
}
```

### Benefits of Higher-Order Functions

1. **Code Reusability** - Write generic algorithms that work with different behaviors
2. **Abstraction** - Separate "what to do" from "how to do it"
3. **Composability** - Combine small functions into larger operations
4. **Readability** - Express intent clearly and concisely
5. **Flexibility** - Change behavior without modifying function structure

**English Summary**: Higher-order functions take functions as parameters or return functions as results. They enable functional programming patterns, code reusability, and abstraction. Kotlin's standard library (map, filter, reduce) extensively uses them. The `inline` keyword helps reduce performance overhead by inlining function and lambda bodies at compile time where applicable.

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого подхода от Java?
- Когда вы бы использовали функции высшего порядка на практике?
- Какие распространенные подводные камни следует учитывать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Функции высшего порядка и лямбды - документация Kotlin](https://kotlinlang.org/docs/lambdas.html)
- [Inline-функции - документация Kotlin](https://kotlinlang.org/docs/inline-functions.html)
- [Практическое руководство по модификатору inline в Kotlin](https://maxkim.eu/a-practical-guide-to-kotlins-inline-modifier)
- [Inline function: Kotlin (статья)](https://agrawalsuneet.medium.com/inline-function-kotlin-3f05d2ea1b59)

## References
- [Higher-Order Functions and Lambdas - Kotlin Documentation](https://kotlinlang.org/docs/lambdas.html)
- [Inline functions - Kotlin Documentation](https://kotlinlang.org/docs/inline-functions.html)
- [A Practical Guide to Kotlin's inline Modifier](https://maxkim.eu/a-practical-guide-to-kotlins-inline-modifier)
- [Inline function: Kotlin](https://agrawalsuneet.medium.com/inline-function-kotlin-3f05d2ea1b59)

## Связанные Вопросы (RU)

- [[q-kotlin-lambda-expressions--kotlin--medium]]
- [[q-kotlin-inline-functions--kotlin--medium]]
- [[q-kotlin-scope-functions--kotlin--medium]]

## Related Questions
- [[q-kotlin-lambda-expressions--kotlin--medium]]
- [[q-kotlin-inline-functions--kotlin--medium]]
- [[q-kotlin-scope-functions--kotlin--medium]]

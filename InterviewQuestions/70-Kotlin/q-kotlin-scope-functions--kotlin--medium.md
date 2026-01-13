---
id: kotlin-014
title: Kotlin Scope Functions / Функции области видимости в Kotlin
aliases:
- Kotlin Scope Functions
- Функции области видимости в Kotlin
topic: kotlin
subtopics:
- apply
- let
- scope-functions
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository
status: draft
moc: moc-kotlin
related:
- c-kotlin
- q-testing-coroutines-runtest--kotlin--medium
created: 2025-10-05
updated: 2025-11-09
tags:
- also
- apply
- difficulty/medium
- kotlin
- let
- run
- scope-functions
- with
anki_cards:
- slug: kotlin-014-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
  - apply
  - let
  - scope-functions
- slug: kotlin-014-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
  - apply
  - let
  - scope-functions
---
# Вопрос (RU)
> Что такое функции области видимости (scope functions) в Kotlin?

---

# Question (EN)
> What are scope functions in Kotlin?

## Ответ (RU)

Стандартная библиотека Kotlin содержит несколько функций, единственная цель которых — выполнить блок кода в контексте объекта. Когда вы вызываете такую функцию на объекте с предоставленным лямбда-выражением, она формирует временную область видимости. В этой области видимости вы можете получить доступ к объекту без его имени. Такие функции называются **функциями области видимости**. Их пять: `let`, `run`, `with`, `apply` и `also`.

Вот типичное использование функции области видимости:

```kotlin
Person("Alice", 20, "Amsterdam").let {
    println(it)
    it.moveTo("London")
    it.incrementAge()
    println(it)
}
```

Функции области видимости не вводят никаких новых технических возможностей, но они могут сделать ваш код более кратким и читаемым.

Из-за схожей природы функций области видимости выбор правильной для вашего случая может быть немного сложным. Выбор в основном зависит от вашего намерения и согласованности использования в вашем проекте.

### Различия

Поскольку функции области видимости все довольно похожи по своей природе, важно понимать различия между ними. Существует два основных различия между каждой функцией области видимости:

- Способ обращения к контекстному объекту
- Возвращаемое значение

#### Контекстный Объект: This Или it

Внутри лямбды функции области видимости контекстный объект доступен по короткой ссылке вместо его фактического имени. Каждая функция области видимости использует один из двух способов доступа к контекстному объекту: как получатель лямбды (`this`) или как аргумент лямбды (`it`)

```kotlin
fun main() {
    val str = "Hello"
    // this
    str.run {
        println("The receiver string length: $length")
        //println("The receiver string length: ${this.length}") // делает то же самое
    }

    // it
    str.let {
        println("The receiver string's length is ${it.length}")
    }
}
```

**this**. `run`, `with` и `apply` ссылаются на контекстный объект как на получателя лямбды - по ключевому слову `this`. Следовательно, в их лямбдах объект доступен так, как он был бы доступен в обычных функциях класса. В большинстве случаев вы можете опустить `this` при доступе к членам объекта-получателя, делая код короче. С другой стороны, если `this` опущен, может быть трудно отличить члены получателя от внешних объектов или функций. Таким образом, наличие контекстного объекта в качестве получателя (`this`) рекомендуется для лямбд, которые в основном работают с членами объекта: вызывают его функции или присваивают свойства.

**it**. В свою очередь, `let` и `also` имеют контекстный объект в качестве аргумента лямбды. Если имя аргумента не указано, к объекту осуществляется доступ по неявному имени по умолчанию `it`. `it` короче, чем `this`, и выражения с `it` обычно легче читать. Однако при вызове функций или свойств объекта у вас нет объекта, доступного неявно, как `this`. Следовательно, наличие контекстного объекта в качестве `it` лучше, когда объект в основном используется в качестве аргумента в вызовах функций. `it` также лучше, если вы используете несколько переменных в блоке кода.

#### Возвращаемое Значение

Функции области видимости различаются результатом, который они возвращают:
- `apply` и `also` возвращают контекстный объект.
- `let`, `run` и `with` возвращают результат лямбды.

Возвращаемое значение `apply` и `also` — это сам контекстный объект. Следовательно, они могут быть включены в цепочки вызовов в качестве побочных шагов: вы можете продолжить связывание вызовов функций на том же объекте после них.

```kotlin
val numberList = mutableListOf<Double>()
numberList.also { println("Populating the list") }
    .apply {
        add(2.71)
        add(3.14)
        add(1.0)
    }
    .also { println("Sorting the list") }
    .sort()
```

Они также могут использоваться в операторах `return` функций, возвращающих контекстный объект.

```kotlin
fun getRandomInt(): Int {
    return Random.nextInt(100).also {
        writeToLog("getRandomInt() generated value $it")
    }
}

val i = getRandomInt()
```

`let`, `run` и `with` возвращают результат лямбды. Таким образом, вы можете использовать их при присвоении результата переменной, связывании операций над результатом и так далее.

```kotlin
val numbers = mutableListOf("one", "two", "three")
val countEndsWithE = numbers.run {
    add("four")
    add("five")
    count { it.endsWith("e") }
}
println("There are $countEndsWithE elements that end with e.")
```

Кроме того, вы можете игнорировать возвращаемое значение и использовать функцию области видимости для создания временной области видимости для переменных.

```kotlin
val numbers = mutableListOf("one", "two", "three")
with(numbers) {
    val firstItem = first()
    val lastItem = last()
    println("First item: $firstItem, last item: $lastItem")
}
```

### Функции

#### Let

**Контекстный объект** доступен как аргумент (`it`). **Возвращаемое значение** — результат лямбды.

`let` может использоваться для вызова одной или нескольких функций на результатах цепочек вызовов. Например, следующий код выводит результаты двух операций над коллекцией:

```kotlin
val numbers = mutableListOf("one", "two", "three", "four", "five")
val resultList = numbers.map { it.length }.filter { it > 3 }
println(resultList)
```

С `let` вы можете переписать это:

```kotlin
val numbers = mutableListOf("one", "two", "three", "four", "five")
numbers.map { it.length }.filter { it > 3 }.let {
    println(it)
    // и больше вызовов функций если нужно
}
```

`let` часто используется для выполнения блока кода только с non-null значениями. Чтобы выполнить действия на non-null объекте, используйте оператор безопасного вызова `?.` на нем и вызовите `let` с действиями в его лямбде.

```kotlin
val str: String? = "Hello"
//processNonNullString(str)       // ошибка компиляции: str может быть null
val length = str?.let {
    println("let() called on $it")
    processNonNullString(it)      // OK: 'it' не null внутри '?.let { }'
    it.length
}
```

Другой случай использования `let` — введение локальных переменных с ограниченной областью видимости для улучшения читаемости кода. Чтобы определить новую переменную для контекстного объекта, укажите её имя в качестве аргумента лямбды, чтобы она могла использоваться вместо `it` по умолчанию.

```kotlin
val numbers = listOf("one", "two", "three", "four")
val modifiedFirstItem = numbers.first().let { firstItem ->
    println("The first item of the list is '$firstItem'")
    if (firstItem.length >= 5) firstItem else "!" + firstItem + "!"
}.toUpperCase()
println("First item after modifications: '$modifiedFirstItem'")
```

#### With

Функция-не-расширение: **контекстный объект** передается в качестве аргумента, но внутри лямбды он доступен как получатель (`this`). **Возвращаемое значение** — результат лямбды.

Мы рекомендуем `with` для вызова функций на контекстном объекте без предоставления результата лямбды. В коде `with` можно читать как "с этим объектом, сделай следующее."

```kotlin
val numbers = mutableListOf("one", "two", "three")
with(numbers) {
    println("'with' is called with argument $this")
    println("It contains $size elements")
}
```

Другой случай использования `with` — введение вспомогательного объекта, свойства или функции которого будут использоваться для вычисления значения.

```kotlin
val numbers = mutableListOf("one", "two", "three")
val firstAndLast = with(numbers) {
    "The first element is ${first()}," +
    " the last element is ${last()}"
}
println(firstAndLast)
```

#### Run

**Контекстный объект** доступен как получатель (`this`). **Возвращаемое значение** — результат лямбды.

`run` делает то же самое, что `with`, но вызывается как `let` - как функция-расширение контекстного объекта.

`run` полезен, когда ваша лямбда содержит как инициализацию объекта, так и вычисление возвращаемого значения.

```kotlin
val service = MultiportService("https://example.kotlinlang.org", 80)

val result = service.run {
    port = 8080
    query(prepareRequest() + " to port $port")
}

// тот же код написанный с функцией let():
val letResult = service.let {
    it.port = 8080
    it.query(it.prepareRequest() + " to port ${it.port}")
}
```

Помимо вызова `run` на объекте-получателе, вы можете использовать его как функцию-не-расширение. Функция-не-расширение `run` позволяет выполнить блок из нескольких операторов там, где требуется выражение.

```kotlin
val hexNumberRegex = run {
    val digits = "0-9"
    val hexDigits = "A-Fa-f"
    val sign = "+-"

    Regex("[$sign]?[$digits$hexDigits]+")
}

for (match in hexNumberRegex.findAll("+1234 -FFFF not-a-number")) {
    println(match.value)
}
```

#### Apply

**Контекстный объект** доступен как получатель (`this`). **Возвращаемое значение** — сам объект.

Используйте `apply` для блоков кода, которые не возвращают значение и в основном работают с членами объекта-получателя. Общий случай для `apply` — конфигурация объекта. Такие вызовы можно читать как "применить следующие присваивания к объекту."

```kotlin
val adam = Person("Adam").apply {
    age = 32
    city = "London"
}
println(adam)
```

Имея получателя в качестве возвращаемого значения, вы можете легко включить `apply` в цепочки вызовов для более сложной обработки.

#### Also

**Контекстный объект** доступен как аргумент (`it`). **Возвращаемое значение** — сам объект.

`also` хорош для выполнения некоторых действий, которые принимают контекстный объект в качестве аргумента. Используйте `also` для действий, которым нужна ссылка скорее на объект, чем на его свойства и функции, или когда вы не хотите затенить ссылку `this` из внешней области видимости.

Когда вы видите `also` в коде, вы можете прочитать это как "и также сделать следующее с объектом."

```kotlin
val numbers = mutableListOf("one", "two", "three")
numbers
    .also { println("The list elements before adding new one: $it") }
    .add("four")
```

### Выбор Функции

Вот краткое руководство по выбору функций области видимости в зависимости от предполагаемой цели:

- Выполнение лямбды на non-null объектах: `let`
- Введение выражения как переменной в локальную область видимости: `let`
- Конфигурация объекта: `apply`
- Конфигурация объекта и вычисление результата: `run`
- Выполнение операторов где требуется выражение: функция-не-расширение `run`
- Дополнительные эффекты: `also`
- Группировка вызовов функций на объекте: `with`

---

## Answer (EN)

The Kotlin standard library contains several functions whose sole purpose is to execute a block of code within the context of an object. When you call such a function on an object with a lambda expression provided, it forms a temporary scope. In this scope, you can access the object without its name. Such functions are called **scope functions**. There are five of them: `let`, `run`, `with`, `apply`, and `also`.

Here's a typical usage of a scope function:

```kotlin
Person("Alice", 20, "Amsterdam").let {
    println(it)
    it.moveTo("London")
    it.incrementAge()
    println(it)
}
```

The scope functions do not introduce any new technical capabilities, but they can make your code more concise and readable.

Due to the similar nature of scope functions, choosing the right one for your case can be a bit tricky. The choice mainly depends on your intent and the consistency of use in your project.

### Distinctions

Because the scope functions are all quite similar in nature, it's important to understand the differences between them. There are two main differences between each scope function:

- The way to refer to the context object
- The return value

#### Context Object: This or it

Inside the lambda of a scope function, the context object is available by a short reference instead of its actual name. Each scope function uses one of two ways to access the context object: as a lambda receiver (`this`) or as a lambda argument (`it`)

```kotlin
fun main() {
    val str = "Hello"
    // this
    str.run {
        println("The receiver string length: $length")
        //println("The receiver string length: ${this.length}") // does the same
    }

    // it
    str.let {
        println("The receiver string's length is ${it.length}")
    }
}
```

**this**. `run`, `with`, and `apply` refer to the context object as a lambda receiver - by keyword `this`. Hence, in their lambdas, the object is available as it would be in ordinary class functions. In most cases, you can omit `this` when accessing the members of the receiver object, making the code shorter. On the other hand, if `this` is omitted, it can be hard to distinguish between the receiver members and external objects or functions. So, having the context object as a receiver (`this`) is recommended for lambdas that mainly operate on the object members: call its functions or assign properties.

**it**. In turn, `let` and `also` have the context object as a lambda argument. If the argument name is not specified, the object is accessed by the implicit default name `it`. `it` is shorter than `this` and expressions with `it` are usually easier for reading. However, when calling the object functions or properties you don't have the object available implicitly like `this`. Hence, having the context object as `it` is better when the object is mostly used as an argument in function calls. `it` is also better if you use multiple variables in the code block.

#### Return Value

The scope functions differ by the result they return:
- `apply` and `also` return the context object.
- `let`, `run`, and `with` return the lambda result.

The return value of `apply` and `also` is the context object itself. Hence, they can be included into call chains as side steps: you can continue chaining function calls on the same object after them.

```kotlin
val numberList = mutableListOf<Double>()
numberList.also { println("Populating the list") }
    .apply {
        add(2.71)
        add(3.14)
        add(1.0)
    }
    .also { println("Sorting the list") }
    .sort()
```

They also can be used in return statements of functions returning the context object.

```kotlin
fun getRandomInt(): Int {
    return Random.nextInt(100).also {
        writeToLog("getRandomInt() generated value $it")
    }
}

val i = getRandomInt()
```

`let`, `run`, and `with` return the lambda result. So, you can use them when assigning the result to a variable, chaining operations on the result, and so on.

```kotlin
val numbers = mutableListOf("one", "two", "three")
val countEndsWithE = numbers.run {
    add("four")
    add("five")
    count { it.endsWith("e") }
}
println("There are $countEndsWithE elements that end with e.")
```

Additionally, you can ignore the return value and use a scope function to create a temporary scope for variables.

```kotlin
val numbers = mutableListOf("one", "two", "three")
with(numbers) {
    val firstItem = first()
    val lastItem = last()
    println("First item: $firstItem, last item: $lastItem")
}
```

### Functions

#### Let

**The context object** is available as an argument (`it`). **The return value** is the lambda result.

`let` can be used to invoke one or more functions on results of call chains. For example, the following code prints the results of two operations on a collection:

```kotlin
val numbers = mutableListOf("one", "two", "three", "four", "five")
val resultList = numbers.map { it.length }.filter { it > 3 }
println(resultList)
```

With `let`, you can rewrite it:

```kotlin
val numbers = mutableListOf("one", "two", "three", "four", "five")
numbers.map { it.length }.filter { it > 3 }.let {
    println(it)
    // and more function calls if needed
}
```

`let` is often used for executing a code block only with non-null values. To perform actions on a non-null object, use the safe call operator `?.` on it and call `let` with the actions in its lambda.

```kotlin
val str: String? = "Hello"
//processNonNullString(str)       // compilation error: str can be null
val length = str?.let {
    println("let() called on $it")
    processNonNullString(it)      // OK: 'it' is not null inside '?.let { }'
    it.length
}
```

Another case for using `let` is introducing local variables with a limited scope for improving code readability. To define a new variable for the context object, provide its name as the lambda argument so that it can be used instead of the default `it`.

```kotlin
val numbers = listOf("one", "two", "three", "four")
val modifiedFirstItem = numbers.first().let { firstItem ->
    println("The first item of the list is '$firstItem'")
    if (firstItem.length >= 5) firstItem else "!" + firstItem + "!"
}.toUpperCase()
println("First item after modifications: '$modifiedFirstItem'")
```

#### With

A non-extension function: **the context object** is passed as an argument, but inside the lambda, it's available as a receiver (`this`). **The return value** is the lambda result.

We recommend `with` for calling functions on the context object without providing the lambda result. In the code, `with` can be read as "with this object, do the following."

```kotlin
val numbers = mutableListOf("one", "two", "three")
with(numbers) {
    println("'with' is called with argument $this")
    println("It contains $size elements")
}
```

Another use case for `with` is introducing a helper object whose properties or functions will be used for calculating a value.

```kotlin
val numbers = mutableListOf("one", "two", "three")
val firstAndLast = with(numbers) {
    "The first element is ${first()}," +
    " the last element is ${last()}"
}
println(firstAndLast)
```

#### Run

**The context object** is available as a receiver (`this`). **The return value** is the lambda result.

`run` does the same as `with` but invokes as `let` - as an extension function of the context object.

`run` is useful when your lambda contains both the object initialization and the computation of the return value.

```kotlin
val service = MultiportService("https://example.kotlinlang.org", 80)

val result = service.run {
    port = 8080
    query(prepareRequest() + " to port $port")
}

// the same code written with let() function:
val letResult = service.let {
    it.port = 8080
    it.query(it.prepareRequest() + " to port ${it.port}")
}
```

Besides calling `run` on a receiver object, you can use it as a non-extension function. Non-extension `run` lets you execute a block of several statements where an expression is required.

```kotlin
val hexNumberRegex = run {
    val digits = "0-9"
    val hexDigits = "A-Fa-f"
    val sign = "+-"

    Regex("[$sign]?[$digits$hexDigits]+")
}

for (match in hexNumberRegex.findAll("+1234 -FFFF not-a-number")) {
    println(match.value)
}
```

#### Apply

**The context object** is available as a receiver (`this`). **The return value** is the object itself.

Use `apply` for code blocks that don't return a value and mainly operate on the members of the receiver object. The common case for `apply` is the object configuration. Such calls can be read as "apply the following assignments to the object."

```kotlin
val adam = Person("Adam").apply {
    age = 32
    city = "London"
}
println(adam)
```

Having the receiver as the return value, you can easily include `apply` into call chains for more complex processing.

#### Also

**The context object** is available as an argument (`it`). **The return value** is the object itself.

`also` is good for performing some actions that take the context object as an argument. Use `also` for actions that need a reference rather to the object than to its properties and functions, or when you don't want to shadow `this` reference from an outer scope.

When you see `also` in the code, you can read it as "and also do the following with the object."

```kotlin
val numbers = mutableListOf("one", "two", "three")
numbers
    .also { println("The list elements before adding new one: $it") }
    .add("four")
```

### Function Selection

Here is a short guide for choosing scope functions depending on the intended purpose:

- Executing a lambda on non-null objects: `let`
- Introducing an expression as a variable in local scope: `let`
- Object configuration: `apply`
- Object configuration and computing the result: `run`
- Running statements where an expression is required: non-extension `run`
- Additional effects: `also`
- Grouping function calls on an object: `with`

## Дополнительные Вопросы (RU)

- Каковы ключевые отличия этого подхода от Java?
- Когда вы бы использовали это на практике?
- Какие распространенные ошибки следует избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Scope functions](https://kotlinlang.org/docs/reference/scope-functions.html)
- [[c-kotlin]]

## References

- [Scope functions](https://kotlinlang.org/docs/reference/scope-functions.html)
- [[c-kotlin]]

## Связанные Вопросы (RU)

- [[q-kotlin-extension-functions--kotlin--medium]]
- [[q-kotlin-null-safety--kotlin--medium]]

## Related Questions

- [[q-kotlin-extension-functions--kotlin--medium]]
- [[q-kotlin-null-safety--kotlin--medium]]

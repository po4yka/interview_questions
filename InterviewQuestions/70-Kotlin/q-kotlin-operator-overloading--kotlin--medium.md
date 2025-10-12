---
id: 20251005-222655
title: "Kotlin Operator Overloading / Перегрузка операторов в Kotlin"
aliases: []

# Classification
topic: kotlin
subtopics: [operators, overloading, conventions, language-features]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-kotlin
related: []

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [kotlin, operators, overloading, conventions, difficulty/medium]
---
# Question (EN)
> What do you know about operator overloading in Kotlin?
# Вопрос (RU)
> Что вы знаете о перегрузке операторов в Kotlin?

---

## Answer (EN)

Kotlin allows you to provide custom implementations for the predefined set of operators on types. These operators have predefined symbolic representation (like `+` or `*`) and precedence. To implement an operator, provide a member function or an extension function with a specific name for the corresponding type. This type becomes the left-hand side type for binary operations and the argument type for the unary ones.

To overload an operator, mark the corresponding function with the `operator` modifier:

```kotlin
interface IndexedContainer {
    operator fun get(index: Int)
}
```

When overriding your operator overloads, you can omit `operator`:

```kotlin
class OrdersList: IndexedContainer {
    override fun get(index: Int) { /*...*/ }
}
```

The following operators can be overloaded:
- Unary prefix operators
- Increments and decrements
- Arithmetic operators
- Indexed access operator
- Invoke operator
- Augmented assignments
- Equality and inequality operators
- Comparison operators

### Unary prefix operators

| Expression | Translated to    |
|------------|------------------|
| `+a`       | `a.unaryPlus()`  |
| `-a`       | `a.unaryMinus()` |
| `!a`       | `a.not()`        |

This table says that when the compiler processes, for example, an expression `+a`, it performs the following steps:
- Determines the type of `a`, let it be `T`;
- Looks up a function `unaryPlus()` with the operator modifier and no parameters for the receiver `T`, that means a member function or an extension function;
- If the function is absent or ambiguous, it is a compilation error;
- If the function is present and its return type is `R`, the expression `+a` has type `R`.

As an example, here's how you can overload the unary minus operator:

```kotlin
data class Point(val x: Int, val y: Int)

operator fun Point.unaryMinus() = Point(-x, -y)

val point = Point(10, 20)

fun main() {
   println(-point)  // prints "Point(x=-10, y=-20)"
}
```

### Arithmetic operators

| Expression | Translated to   |
|------------|-----------------|
| `a + b`    | `a.plus(b)`     |
| `a - b`    | `a.minus(b)`    |
| `a * b`    | `a.times(b)`    |
| `a / b`    | `a.div(b)`      |
| `a % b`    | `a.rem(b)`      |
| `a..b`     | `a.rangeTo(b)`  |
| `a..<b`    | `a.rangeUntil(b)` |

For the operations in this table, the compiler just resolves the expression in the **Translated to** column.

Example:

```kotlin
fun main(args: Array<String>) {
    val p1 = Point(3, -8)
    val p2 = Point(2, 9)

    var sum = Point()
    sum = p1 + p2

    println("sum = (${sum.x}, ${sum.y})")
}

class Point(val x: Int = 0, val y: Int = 10) {

    // overloading plus function
    operator fun plus(p: Point) : Point {
        return Point(x + p.x, y + p.y)
    }
}
```

When you run the program, the output will be:
```
sum = (5, 1)
```

### Indexed access operator

| Expression             | Translated to              |
|------------------------|----------------------------|
| `a[i]`                 | `a.get(i)`                 |
| `a[i, j]`              | `a.get(i, j)`              |
| `a[i_1, ..., i_n]`     | `a.get(i_1, ..., i_n)`     |
| `a[i] = b`             | `a.set(i, b)`              |
| `a[i, j] = b`          | `a.set(i, j, b)`           |
| `a[i_1, ..., i_n] = b` | `a.set(i_1, ..., i_n, b)`  |

Square brackets are translated to calls to `get` and `set` with appropriate numbers of arguments.

### Invoke operator

| Expression           | Translated to            |
|----------------------|--------------------------|
| `a()`                | `a.invoke()`             |
| `a(i)`               | `a.invoke(i)`            |
| `a(i, j)`            | `a.invoke(i, j)`         |
| `a(i_1, ..., i_n)`   | `a.invoke(i_1, ..., i_n)` |

Parentheses are translated to calls to `invoke` with appropriate number of arguments.

Specifying an invoke operator on a class allows it to be called on *any instances of the class without a method name*.

Let's see this in action:

```kotlin
class Greeter(val greeting: String) {
    operator fun invoke(name: String) {
        println("$greeting $name")
    }
}

fun main(args: Array<String>) {
    val greeter = Greeter(greeting = "Welcome")
    greeter(name = "Kotlin")
    //this calls the invoke function which takes String as a parameter
}
```

### Augmented assignments

| Expression | Translated to       |
|------------|---------------------|
| `a += b`   | `a.plusAssign(b)`   |
| `a -= b`   | `a.minusAssign(b)`  |
| `a *= b`   | `a.timesAssign(b)`  |
| `a /= b`   | `a.divAssign(b)`    |
| `a %= b`   | `a.remAssign(b)`    |

For the assignment operations, for example `a += b`, the compiler performs the following steps:
- If the function from the right column is available:
  - If the corresponding binary function (that means `plus()` for `plusAssign()`) is available too, `a` is a mutable variable, and the return type of `plus` is a subtype of the type of `a`, report an error (ambiguity);
  - Make sure its return type is `Unit`, and report an error otherwise;
  - Generate code for `a.plusAssign(b)`.
- Otherwise, try to generate code for `a = a + b` (this includes a type check: the type of `a + b` must be a subtype of `a`).

### Equality and inequality operators

| Expression | Translated to                      |
|------------|------------------------------------|
| `a == b`   | `a?.equals(b) ?: (b === null)`     |
| `a != b`   | `!(a?.equals(b) ?: (b === null))`  |

These operators only work with the function `equals(other: Any?): Boolean`, which can be overridden to provide custom equality check implementation. Any other function with the same name (like `equals(other: Foo)`) will not be called.

### Comparison operators

| Expression | Translated to        |
|------------|----------------------|
| `a > b`    | `a.compareTo(b) > 0` |
| `a < b`    | `a.compareTo(b) < 0` |
| `a >= b`   | `a.compareTo(b) >= 0`|
| `a <= b`   | `a.compareTo(b) <= 0`|

All comparisons are translated into calls to `compareTo`, that is required to return `Int`.

## Ответ (RU)

Kotlin позволяет предоставлять пользовательские реализации для предопределенного набора операторов для типов. Эти операторы имеют предопределенное символьное представление (например, `+` или `*`) и приоритет. Чтобы реализовать оператор, предоставьте функцию-член или функцию-расширение с определенным именем для соответствующего типа. Этот тип становится типом левой части для бинарных операций и типом аргумента для унарных.

Чтобы перегрузить оператор, пометьте соответствующую функцию модификатором `operator`:

```kotlin
interface IndexedContainer {
    operator fun get(index: Int)
}
```

При переопределении перегрузок операторов вы можете опустить `operator`:

```kotlin
class OrdersList: IndexedContainer {
    override fun get(index: Int) { /*...*/ }
}
```

Следующие операторы могут быть перегружены:
- Унарные префиксные операторы
- Инкременты и декременты
- Арифметические операторы
- Оператор индексированного доступа
- Оператор invoke
- Дополненные присваивания
- Операторы равенства и неравенства
- Операторы сравнения

### Унарные префиксные операторы

| Выражение  | Переводится в    |
|------------|------------------|
| `+a`       | `a.unaryPlus()`  |
| `-a`       | `a.unaryMinus()` |
| `!a`       | `a.not()`        |

Эта таблица говорит, что когда компилятор обрабатывает, например, выражение `+a`, он выполняет следующие шаги:
- Определяет тип `a`, пусть это будет `T`;
- Ищет функцию `unaryPlus()` с модификатором operator и без параметров для получателя `T`, что означает функцию-член или функцию-расширение;
- Если функция отсутствует или неоднозначна, это ошибка компиляции;
- Если функция присутствует и её тип возврата `R`, выражение `+a` имеет тип `R`.

В качестве примера, вот как вы можете перегрузить оператор унарного минуса:

```kotlin
data class Point(val x: Int, val y: Int)

operator fun Point.unaryMinus() = Point(-x, -y)

val point = Point(10, 20)

fun main() {
   println(-point)  // выводит "Point(x=-10, y=-20)"
}
```

### Арифметические операторы

| Выражение  | Переводится в    |
|------------|------------------|
| `a + b`    | `a.plus(b)`      |
| `a - b`    | `a.minus(b)`     |
| `a * b`    | `a.times(b)`     |
| `a / b`    | `a.div(b)`       |
| `a % b`    | `a.rem(b)`       |
| `a..b`     | `a.rangeTo(b)`   |
| `a..<b`    | `a.rangeUntil(b)`|

Для операций в этой таблице компилятор просто разрешает выражение в столбце **Переводится в**.

Пример:

```kotlin
fun main(args: Array<String>) {
    val p1 = Point(3, -8)
    val p2 = Point(2, 9)

    var sum = Point()
    sum = p1 + p2

    println("sum = (${sum.x}, ${sum.y})")
}

class Point(val x: Int = 0, val y: Int = 10) {

    // перегрузка функции plus
    operator fun plus(p: Point) : Point {
        return Point(x + p.x, y + p.y)
    }
}
```

Когда вы запустите программу, вывод будет:
```
sum = (5, 1)
```

### Оператор индексированного доступа

| Выражение              | Переводится в              |
|------------------------|----------------------------|
| `a[i]`                 | `a.get(i)`                 |
| `a[i, j]`              | `a.get(i, j)`              |
| `a[i_1, ..., i_n]`     | `a.get(i_1, ..., i_n)`     |
| `a[i] = b`             | `a.set(i, b)`              |
| `a[i, j] = b`          | `a.set(i, j, b)`           |
| `a[i_1, ..., i_n] = b` | `a.set(i_1, ..., i_n, b)`  |

Квадратные скобки переводятся в вызовы `get` и `set` с соответствующим количеством аргументов.

### Оператор invoke

| Выражение            | Переводится в             |
|----------------------|---------------------------|
| `a()`                | `a.invoke()`              |
| `a(i)`               | `a.invoke(i)`             |
| `a(i, j)`            | `a.invoke(i, j)`          |
| `a(i_1, ..., i_n)`   | `a.invoke(i_1, ..., i_n)` |

Круглые скобки переводятся в вызовы `invoke` с соответствующим количеством аргументов.

Указание оператора invoke для класса позволяет вызывать его на *любых экземплярах класса без имени метода*.

Давайте посмотрим на это в действии:

```kotlin
class Greeter(val greeting: String) {
    operator fun invoke(name: String) {
        println("$greeting $name")
    }
}

fun main(args: Array<String>) {
    val greeter = Greeter(greeting = "Welcome")
    greeter(name = "Kotlin")
    //это вызывает функцию invoke, которая принимает String в качестве параметра
}
```

### Дополненные присваивания

| Выражение  | Переводится в       |
|------------|---------------------|
| `a += b`   | `a.plusAssign(b)`   |
| `a -= b`   | `a.minusAssign(b)`  |
| `a *= b`   | `a.timesAssign(b)`  |
| `a /= b`   | `a.divAssign(b)`    |
| `a %= b`   | `a.remAssign(b)`    |

Для операций присваивания, например `a += b`, компилятор выполняет следующие шаги:
- Если функция из правого столбца доступна:
  - Если соответствующая бинарная функция (это означает `plus()` для `plusAssign()`) также доступна, `a` является изменяемой переменной, и тип возврата `plus` является подтипом типа `a`, сообщить об ошибке (неоднозначность);
  - Убедиться, что её тип возврата `Unit`, и сообщить об ошибке в противном случае;
  - Сгенерировать код для `a.plusAssign(b)`.
- В противном случае попытаться сгенерировать код для `a = a + b` (это включает проверку типа: тип `a + b` должен быть подтипом `a`).

### Операторы равенства и неравенства

| Выражение  | Переводится в                      |
|------------|------------------------------------|
| `a == b`   | `a?.equals(b) ?: (b === null)`     |
| `a != b`   | `!(a?.equals(b) ?: (b === null))`  |

Эти операторы работают только с функцией `equals(other: Any?): Boolean`, которая может быть переопределена для предоставления пользовательской реализации проверки равенства. Любая другая функция с таким же именем (например, `equals(other: Foo)`) не будет вызвана.

### Операторы сравнения

| Выражение  | Переводится в        |
|------------|----------------------|
| `a > b`    | `a.compareTo(b) > 0` |
| `a < b`    | `a.compareTo(b) < 0` |
| `a >= b`   | `a.compareTo(b) >= 0`|
| `a <= b`   | `a.compareTo(b) <= 0`|

Все сравнения переводятся в вызовы `compareTo`, которая должна возвращать `Int`.

---

## References
- [Operator overloading](https://kotlinlang.org/docs/operator-overloading.html)
- [Kotlin Operator Overloading](https://www.programiz.com/kotlin-programming/operator-overloading)
- [Invoke Operator & Operator Overloading in Kotlin](https://stackoverflow.com/questions/45173677/invoke-operator-operator-overloading-in-kotlin)
- [Operator overloading in Kotlin](https://kt.academy/article/kfde-operators)
- [How Can Kotlin Operator Overloading Help You?](https://codersee.com/how-can-kotlin-operator-overloading-help-you/)

## Related Questions

### Prerequisites (Easier)
- [[q-equality-operators-kotlin--kotlin--easy]] - Equality

### Related (Medium)
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-kotlin-collections--kotlin--medium]] - Collections
- [[q-backpressure-in-kotlin-flow--programming-languages--medium]] - Flow

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-operators-deep-dive--kotlin--hard]] - Flow
- [[q-flow-backpressure-strategies--kotlin--hard]] - Flow
### Prerequisites (Easier)
- [[q-equality-operators-kotlin--kotlin--easy]] - Equality

### Related (Medium)
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-kotlin-collections--kotlin--medium]] - Collections
- [[q-backpressure-in-kotlin-flow--programming-languages--medium]] - Flow

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-operators-deep-dive--kotlin--hard]] - Flow
- [[q-flow-backpressure-strategies--kotlin--hard]] - Flow
### Prerequisites (Easier)
- [[q-equality-operators-kotlin--kotlin--easy]] - Equality

### Related (Medium)
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-kotlin-collections--kotlin--medium]] - Collections
- [[q-backpressure-in-kotlin-flow--programming-languages--medium]] - Flow

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-operators-deep-dive--kotlin--hard]] - Flow
- [[q-flow-backpressure-strategies--kotlin--hard]] - Flow
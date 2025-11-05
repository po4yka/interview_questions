---
id: kotlin-008
title: "Kotlin Null Safety / Null-безопасность в Kotlin"
aliases: ["Kotlin Null Safety, Null-безопасность в Kotlin"]

# Classification
topic: kotlin
subtopics: [null-safety, nullability, safe-calls]
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
related: [q-flow-exception-handling--kotlin--medium, q-kotlin-class-initializers--programming-languages--medium, q-kotlin-non-inheritable-class--programming-languages--easy]

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [difficulty/medium, kotlin, null-safety, nullability, safe-calls, types]
date created: Sunday, October 12th 2025, 12:27:46 pm
date modified: Saturday, November 1st 2025, 5:43:25 pm
---
# Вопрос (RU)
> Опишите nullability и null-безопасность в Kotlin

---

# Question (EN)
> Describe nullability and null safety in Kotlin
## Ответ (RU)

*Nullability* — это способность переменной содержать значение `null`. Когда переменная содержит `null`, попытка разыменовать переменную приводит к `NullPointerException`. Существует много способов написания кода для минимизации вероятности получения исключений нулевого указателя.

### Поддержка Nullable Типов

Наиболее важное отличие между системами типов Kotlin и Java — это явная поддержка nullable типов в Kotlin. Это способ указать, какие переменные могут содержать значение `null`. Если переменная может быть `null`, небезопасно вызывать метод на переменной, потому что это может вызвать `NullPointerException`. Kotlin запрещает такие вызовы во время компиляции и тем самым предотвращает множество возможных исключений. Во время выполнения объекты nullable типов и объекты non-nullable типов обрабатываются одинаково: nullable тип не является оберткой для non-nullable типа. Все проверки выполняются во время компиляции. Это означает, что почти нет накладных расходов во время выполнения при работе с nullable типами в Kotlin.

В Java, если вы не пишете проверки на null, методы могут выбрасывать `NullPointerException`:

```java
// Java
int stringLength(String a) {
    return a.length();
}

void main() {
    stringLength(null); // Выбрасывает `NullPointerException`
}
```

Этот вызов будет иметь следующий вывод:
```
java.lang.NullPointerException: Cannot invoke "String.length()" because "a" is null
    at test.java.Nullability.stringLength(Nullability.java:8)
    at test.java.Nullability.main(Nullability.java:12)
```

В Kotlin все обычные типы по умолчанию non-nullable, если вы явно не пометите их как nullable. Если вы не ожидаете, что a будет `null`, объявите функцию `stringLength()` следующим образом:

```kotlin
// Kotlin
fun stringLength(a: String) = a.length
```

Параметр `a` имеет тип `String`, что в Kotlin означает, что он всегда должен содержать экземпляр `String` и не может содержать `null`. Nullable типы в Kotlin помечаются знаком вопроса `?`, например, `String?`. Ситуация с `NullPointerException` во время выполнения невозможна, если `a` имеет тип `String`, потому что компилятор обеспечивает правило, что все аргументы `stringLength()` не являются `null`.

Попытка передать значение `null` функции `stringLength(a: String)` приведет к ошибке времени компиляции: "Null can not be a value of a non-null type String".

Если вы хотите использовать эту функцию с любыми аргументами, включая `null`, используйте знак вопроса после типа аргумента `String?` и проверьте внутри тела функции, что значение аргумента не `null`:

```kotlin
// Kotlin
fun stringLength(a: String?): Int = if (a != null) a.length else 0
```

После успешной проверки компилятор обрабатывает переменную так, как если бы она была non-nullable типа `String` в области видимости, где компилятор выполняет проверку.

Вы можете написать то же самое короче – используйте оператор безопасного вызова `?.` (сокращение If-not-null), который позволяет объединить проверку на null и вызов метода в одну операцию:

```kotlin
// Kotlin
fun stringLength(a: String?): Int = a?.length ?: 0
```

### Значения По Умолчанию Вместо Null

Проверка на `null` часто используется в сочетании с установкой значения по умолчанию в случае успешной проверки на null.

Код Java с проверкой на null:

```java
// Java
Order order = findOrder();
if (order == null) {
    order = new Order(new Customer("Antonio"))
}
```

Чтобы выразить то же самое в Kotlin, используйте оператор Elvis (сокращение If-not-null-else):

```kotlin
// Kotlin
val order = findOrder() ?: Order(Customer("Antonio"))
```

### Функции, Возвращающие Значение Или Null

В Java вам нужно быть осторожным при работе с элементами списка. Вы всегда должны проверять, существует ли элемент по индексу, прежде чем пытаться использовать элемент:

```java
// Java
var numbers = new ArrayList<Integer>();
numbers.add(1);
numbers.add(2);

System.out.println(numbers.get(0));
//numbers.get(5) // Exception!
```

Стандартная библиотека Kotlin часто предоставляет функции, имена которых указывают, могут ли они вернуть значение `null`. Это особенно распространено в API коллекций:

```kotlin
// Kotlin
// Тот же код, что и в Java:
val numbers = listOf(1, 2)

println(numbers[0])  // Может выбросить IndexOutOfBoundsException если коллекция пуста
//numbers.get(5)     // Exception!

// Больше возможностей:
println(numbers.firstOrNull())
println(numbers.getOrNull(5)) // null
```

### Безопасное Приведение Типов

Когда вам нужно безопасно привести тип, в Java вы бы использовали оператор `instanceof` и затем проверили, насколько хорошо это сработало:

```java
// Java
int getStringLength(Object y) {
    return y instanceof String x ? x.length() : -1;
}

void main() {
    System.out.println(getStringLength(1)); // Выводит `-1`
}
```

Чтобы избежать исключений в Kotlin, используйте оператор безопасного приведения `as?`, который возвращает `null` при неудаче:

```kotlin
// Kotlin
fun main() {
    println(getStringLength(1)) // Выводит `-1`
}

fun getStringLength(y: Any): Int {
    val x: String? = y as? String // null
    return x?.length ?: -1 // Возвращает -1 потому что `x` равен null
}
```

### Использование let()

Функция `let()` выполняет указанную лямбда-функцию только когда ссылка не является nullable, как показано ниже.

```kotlin
var newString: String? = "Kotlin from Android"
newString?.let { println("The string value is: $it") }
newString = null
newString?.let { println("The string value is: $it") }
```

Оператор внутри let является лямбда-выражением. Он выполняется только когда значение `newString` не `null`. `it` содержит ненулевое значение `newString`.

### Использование also()

`also()` ведет себя так же, как `let()`, за исключением того, что обычно используется для логирования значений. Он не может присвоить значение it другой переменной. Вот пример `let()` и `also()`, связанных вместе.

```kotlin
var c = "Hello"

var newString: String? = "Kotlin from Android"
newString?.let { c = it }.also { println("Logging the value: $it") }
```

---

## Answer (EN)

*Nullability* is the ability of a variable to hold a `null` value. When a variable contains `null`, an attempt to dereference the variable leads to a `NullPointerException`. There are many ways to write code in order to minimize the probability of receiving null pointer exceptions.

### Support for Nullable Types

The most important difference between Kotlin's and Java's type systems is Kotlin's explicit support for nullable types. It is a way to indicate which variables can possibly hold a `null` value. If a variable can be `null`, it's not safe to call a method on the variable because this can cause a `NullPointerException`. Kotlin prohibits such calls at compile time and thereby prevents lots of possible exceptions. At runtime, objects of nullable types and objects of non-nullable types are treated the same: A nullable type isn't a wrapper for a non-nullable type. All checks are performed at compile time. That means there's almost no runtime overhead for working with nullable types in Kotlin.

In Java, if you don't write null checks, methods may throw a `NullPointerException`:

```java
// Java
int stringLength(String a) {
    return a.length();
}

void main() {
    stringLength(null); // Throws a `NullPointerException`
}
```

This call will have the following output:
```
java.lang.NullPointerException: Cannot invoke "String.length()" because "a" is null
    at test.java.Nullability.stringLength(Nullability.java:8)
    at test.java.Nullability.main(Nullability.java:12)
```

In Kotlin, all regular types are non-nullable by default unless you explicitly mark them as nullable. If you don't expect a to be `null`, declare the `stringLength()` function as follows:

```kotlin
// Kotlin
fun stringLength(a: String) = a.length
```

The parameter `a` has the `String` type, which in Kotlin means it must always contain a `String` instance and it cannot contain `null`. Nullable types in Kotlin are marked with a question mark `?`, for example, `String?`. The situation with a `NullPointerException` at runtime is impossible if `a` is `String` because the compiler enforces the rule that all arguments of `stringLength()` not be `null`.

An attempt to pass a `null` value to the `stringLength(a: String)` function will result in a compile-time error, "Null can not be a value of a non-null type String".

If you want to use this function with any arguments, including `null`, use a question mark after the argument type `String?` and check inside the function body to ensure that the value of the argument is not `null`:

```kotlin
// Kotlin
fun stringLength(a: String?): Int = if (a != null) a.length else 0
```

After the check is passed successfully, the compiler treats the variable as if it were of the non-nullable type `String` in the scope where the compiler performs the check.

You can write the same shorter – use the safe-call operator `?.` (If-not-null shorthand), which allows you to combine a null check and a method call into a single operation:

```kotlin
// Kotlin
fun stringLength(a: String?): Int = a?.length ?: 0
```

### Default Values instead of Null

Checking for `null` is often used in combination with setting the default value in case the null check is successful.

The Java code with a null check:

```java
// Java
Order order = findOrder();
if (order == null) {
    order = new Order(new Customer("Antonio"))
}
```

To express the same in Kotlin, use the Elvis operator (If-not-null-else shorthand):

```kotlin
// Kotlin
val order = findOrder() ?: Order(Customer("Antonio"))
```

### Functions Returning a Value or Null

In Java, you need to be careful when working with list elements. You should always check whether an element exists at an index before you attempt to use the element:

```java
// Java
var numbers = new ArrayList<Integer>();
numbers.add(1);
numbers.add(2);

System.out.println(numbers.get(0));
//numbers.get(5) // Exception!
```

The Kotlin standard library often provides functions whose names indicate whether they can possibly return a `null` value. This is especially common in the collections API:

```kotlin
// Kotlin
// The same code as in Java:
val numbers = listOf(1, 2)

println(numbers[0])  // Can throw IndexOutOfBoundsException if the collection is empty
//numbers.get(5)     // Exception!

// More abilities:
println(numbers.firstOrNull())
println(numbers.getOrNull(5)) // null
```

### Casting Types Safely

When you need to safely cast a type, in Java you would use the `instanceof` operator and then check how well it worked:

```java
// Java
int getStringLength(Object y) {
    return y instanceof String x ? x.length() : -1;
}

void main() {
    System.out.println(getStringLength(1)); // Prints `-1`
}
```

To avoid exceptions in Kotlin, use the safe cast operator `as?`, which returns `null` on failure:

```kotlin
// Kotlin
fun main() {
    println(getStringLength(1)) // Prints `-1`
}

fun getStringLength(y: Any): Int {
    val x: String? = y as? String // null
    return x?.length ?: -1 // Returns -1 because `x` is null
}
```

### Using let()

`let()` function executes the lambda function specified only when the reference is non-nullable as shown below.

```kotlin
var newString: String? = "Kotlin from Android"
newString?.let { println("The string value is: $it") }
newString = null
newString?.let { println("The string value is: $it") }
```

The statement inside let is a lambda expression. It's only run when the value of `newString` is not `null`. `it` contains the non-null value of `newString`.

### Using also()

`also()` behaves the same way as `let()` except that it's generally used to log the values. It can't assign the value of it to another variable. Here's an example of `let()` and `also()` chained together.

```kotlin
var c = "Hello"

var newString: String? = "Kotlin from Android"
newString?.let { c = it }.also { println("Logging the value: $it") }
```

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Nullability in Java and Kotlin](https://kotlinlang.org/docs/java-to-kotlin-nullability-guide.html)
- [Null safety](https://kotlinlang.org/docs/null-safety.html)
- [Null safety tutorial](https://kotlinlang.org/docs/tutorials/kotlin-for-py/null-safety.html)

## Related Questions
- [[q-kotlin-lateinit--kotlin--medium]]
- [[q-kotlin-type-system--kotlin--medium]]

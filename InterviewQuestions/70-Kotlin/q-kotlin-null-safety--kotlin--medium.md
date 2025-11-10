---
id: kotlin-008
title: "Kotlin Null Safety / Null-безопасность в Kotlin"
aliases: ["Kotlin Null Safety", "Null-безопасность в Kotlin"]

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
related: [c-kotlin, q-flow-exception-handling--kotlin--medium, q-kotlin-non-inheritable-class--programming-languages--easy]

# Timestamps
created: 2025-10-05
updated: 2025-11-09

tags: [difficulty/medium, kotlin, null-safety, nullability, safe-calls, types]
---
# Вопрос (RU)
> Опишите nullability и null-безопасность в Kotlin

---

# Question (EN)
> Describe nullability and null safety in Kotlin

## Ответ (RU)

*Nullability* — это способность переменной содержать значение `null`. Когда переменная содержит `null`, попытка разыменовать переменную приводит к `NullPointerException`. В Kotlin система типов и встроенные операторы помогают писать код так, чтобы минимизировать вероятность получения `NullPointerException`.

### Поддержка Nullable Типов

Наиболее важное отличие между системами типов Kotlin и Java — это явная поддержка nullable типов в Kotlin. Это способ указать, какие переменные могут содержать значение `null`. Если переменная может быть `null`, небезопасно вызывать метод на переменной без проверки, потому что это может вызвать `NullPointerException`. Kotlin запрещает такие небезопасные вызовы на явно nullable типах на этапе компиляции и тем самым предотвращает множество возможных исключений.

Во время выполнения объекты nullable типов и объекты non-nullable типов обрабатываются одинаково: nullable тип не является оберткой для non-nullable типа. Основные проверки null-безопасности выполняются во время компиляции, поэтому почти нет накладных расходов во время выполнения при работе с nullable типами в Kotlin. Однако `NullPointerException` по-прежнему возможен из других источников (например, platform types из Java, оператор `!!`, ошибки в инициализации и т.д.).

В Java, если вы не пишете проверки на null, методы могут выбрасывать `NullPointerException`:

```java
// Java
int stringLength(String a) {
    return a.length();
}

void main() {
    stringLength(null); // Выбрасывает NullPointerException
}
```

Этот вызов приведет к следующему результату (сообщение может отличаться в разных версиях Java):
```
java.lang.NullPointerException: Cannot invoke "String.length()" because "a" is null
    at test.java.Nullability.stringLength(Nullability.java:8)
    at test.java.Nullability.main(Nullability.java:12)
```

В Kotlin все обычные типы по умолчанию non-nullable, если вы явно не пометите их как nullable. Если вы не ожидаете, что `a` будет `null`, объявите функцию `stringLength()` следующим образом:

```kotlin
// Kotlin
fun stringLength(a: String) = a.length
```

Параметр `a` имеет тип `String`, что в Kotlin означает, что он всегда должен содержать экземпляр `String` и не может содержать `null`. Nullable типы в Kotlin помечаются знаком вопроса `?`, например, `String?`. Компилятор гарантирует, что вы не передадите `null` туда, где ожидается `String`, поэтому при корректном использовании типов `String` (без использования `!!` и небезопасных вызовов из Java) `NullPointerException` из-за `a` не произойдет.

Попытка передать значение `null` функции `stringLength(a: String)` приведет к ошибке времени компиляции: "Null can not be a value of a non-null type String".

Если вы хотите использовать эту функцию с любыми аргументами, включая `null`, используйте знак вопроса после типа аргумента `String?` и проверьте внутри тела функции, что значение аргумента не `null`:

```kotlin
// Kotlin
fun stringLength(a: String?): Int = if (a != null) a.length else 0
```

После успешной проверки компилятор обрабатывает переменную так, как если бы она была non-nullable типа `String` в области видимости, где выполняется эта проверка: происходит умный каст.

Вы можете написать то же самое короче – используйте оператор безопасного вызова `?.` (if-not-null), который позволяет объединить проверку на `null` и вызов метода в одну операцию, и оператор Элвиса `?:` для значения по умолчанию:

```kotlin
// Kotlin
fun stringLength(a: String?): Int = a?.length ?: 0
```

### Значения По Умолчанию Вместо Null

Проверка на `null` часто используется в сочетании с установкой значения по умолчанию, которое применяется, если выражение слева оказалось `null`.

Код Java с проверкой на `null`:

```java
// Java
Order order = findOrder();
if (order == null) {
    order = new Order(new Customer("Antonio"));
}
```

Чтобы выразить то же самое в Kotlin, используйте оператор Элвиса (if-not-null-else):

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
//numbers.get(5); // Exception!
```

(Использование `var` здесь предполагает современную версию Java.)

Стандартная библиотека Kotlin часто предоставляет функции, имена которых указывают, могут ли они вернуть значение `null`. Это особенно распространено в API коллекций:

```kotlin
// Kotlin
// Тот же код, что и в Java:
val numbers = listOf(1, 2)

println(numbers[0])  // Может выбросить IndexOutOfBoundsException, если коллекция пуста или индекс вне диапазона
//numbers[5]         // Exception!

// Более безопасные варианты:
println(numbers.firstOrNull())
println(numbers.getOrNull(5)) // null
```

### Безопасное Приведение Типов

Когда вам нужно безопасно привести тип, в Java вы бы использовали оператор `instanceof` и затем проверили результат:

```java
// Java
int getStringLength(Object y) {
    return y instanceof String x ? x.length() : -1; // Синтаксис сопоставления с образцом, доступный начиная с Java 16+
}

void main() {
    System.out.println(getStringLength(1)); // Выводит -1
}
```

Чтобы избежать исключений в Kotlin, используйте оператор безопасного приведения `as?`, который возвращает `null` при неудаче:

```kotlin
// Kotlin
fun main() {
    println(getStringLength(1)) // Выводит -1
}

fun getStringLength(y: Any): Int {
    val x: String? = y as? String // null, если y не `String`
    return x?.length ?: -1 // Возвращает -1, потому что x == null
}
```

### Использование let()

Функция `let()` — scope function, которая:
- всегда доступна для любого объекта,
- возвращает результат лямбда-выражения,
- часто используется вместе с оператором безопасного вызова `?.let { ... }` для аккуратной обработки nullable значений.

Пример использования с nullable переменной:

```kotlin
var newString: String? = "Kotlin from Android"
newString?.let { println("The string value is: $it") }
newString = null
newString?.let { println("The string value is: $it") } // не выполнится
```

Лямбда внутри `?.let { ... }` выполняется только тогда, когда значение `newString` не `null`. Внутри лямбды `it` имеет не-null тип.

### Использование also()

Функция `also()` — другая scope function. Она:
- всегда доступна для любого объекта,
- возвращает исходный объект (receiver),
- часто используется для логирования или побочных эффектов в цепочках вызовов.

Пример корректного использования с nullable значением и логированием:

```kotlin
var c = "Hello"

var newString: String? = "Kotlin from Android"
newString = newString
    ?.also { println("Logging the value: $it") } // выполняется только если не null
    ?.also { c = it }                             // здесь it имеет не-null тип
```

Обратите внимание: если использовать `newString?.let { ... }.also { ... }`, то `also` будет вызван всегда, а его `it` может оказаться `null`, так как `also` получит результат `let`, а не исходное значение. Это важно понимать, чтобы не делать неверных предположений о nullability.

Также см. [[c-kotlin]].

---

## Answer (EN)

*Nullability* is the ability of a variable to hold a `null` value. When a variable contains `null`, attempting to dereference it leads to a `NullPointerException`. In Kotlin, the type system and built-in operators help you write code that minimizes the likelihood of `NullPointerException`.

### Support for Nullable Types

The most important difference between Kotlin's and Java's type systems is Kotlin's explicit support for nullable types. It's a way to indicate which variables can possibly hold a `null` value. If a variable can be `null`, it's unsafe to call methods or access properties on it without a check, because that can cause a `NullPointerException`. Kotlin prohibits such unsafe calls on explicitly nullable types at compile time, preventing many potential exceptions.

At runtime, objects of nullable types and objects of non-nullable types are treated the same: a nullable type is not a wrapper for a non-nullable type. Most null-safety checks are performed at compile time, so there is almost no runtime overhead for working with nullable types in Kotlin. However, `NullPointerException` is still possible from other sources (for example, platform types coming from Java, the `!!` operator, initialization issues, etc.).

In Java, if you don't write null checks, methods may throw a `NullPointerException`:

```java
// Java
int stringLength(String a) {
    return a.length();
}

void main() {
    stringLength(null); // Throws NullPointerException
}
```

This call may result in an error similar to (the exact message can depend on Java version):
```
java.lang.NullPointerException: Cannot invoke "String.length()" because "a" is null
    at test.java.Nullability.stringLength(Nullability.java:8)
    at test.java.Nullability.main(Nullability.java:12)
```

In Kotlin, all regular types are non-nullable by default unless you explicitly mark them as nullable. If you don't expect `a` to be `null`, declare the `stringLength()` function as follows:

```kotlin
// Kotlin
fun stringLength(a: String) = a.length
```

The parameter `a` has the type `String`, which in Kotlin means it must always contain a `String` instance and cannot contain `null`. Nullable types in Kotlin are marked with a question mark `?`, for example, `String?`. The compiler enforces that you don't pass `null` where `String` is expected, so when you use types correctly (without `!!` and unsafe interop), `NullPointerException` due to `a` is avoided.

An attempt to pass a `null` value to `stringLength(a: String)` will result in a compile-time error: "Null can not be a value of a non-null type String".

If you want to use this function with arguments that may be `null`, use `String?` as the parameter type and check inside the function body that the value is not `null`:

```kotlin
// Kotlin
fun stringLength(a: String?): Int = if (a != null) a.length else 0
```

Once the check passes, the compiler smart-casts the variable to a non-nullable `String` within the scope where the check holds.

You can write the same in a shorter way using the safe-call operator `?.` (if-not-null) to combine the null check and method call, along with the Elvis operator `?:` for a default value:

```kotlin
// Kotlin
fun stringLength(a: String?): Int = a?.length ?: 0
```

### Default Values instead of Null

Checking for `null` is often combined with supplying a default value that is used when the expression on the left is `null`.

Java code with a null check:

```java
// Java
Order order = findOrder();
if (order == null) {
    order = new Order(new Customer("Antonio"));
}
```

To express the same in Kotlin, use the Elvis operator (if-not-null-else):

```kotlin
// Kotlin
val order = findOrder() ?: Order(Customer("Antonio"))
```

### Functions Returning a Value or Null

In Java, you must be careful when working with list elements. You should always check whether an element exists at an index before using it:

```java
// Java
var numbers = new ArrayList<Integer>();
numbers.add(1);
numbers.add(2);

System.out.println(numbers.get(0));
//numbers.get(5); // Exception!
```

(Using `var` here assumes a modern Java version.)

The Kotlin standard library often provides functions whose names indicate whether they can return a `null` value. This is especially common in the collections API:

```kotlin
// Kotlin
// The same code as in Java:
val numbers = listOf(1, 2)

println(numbers[0])  // Can throw IndexOutOfBoundsException if the collection is empty or index is out of bounds
//numbers[5]         // Exception!

// Safer alternatives:
println(numbers.firstOrNull())
println(numbers.getOrNull(5)) // null
```

### Casting Types Safely

When you need to cast safely in Java, you would use the `instanceof` operator and then branch based on the result:

```java
// Java
int getStringLength(Object y) {
    return y instanceof String x ? x.length() : -1; // Java 16+ pattern matching syntax
}

void main() {
    System.out.println(getStringLength(1)); // Prints -1
}
```

To avoid exceptions in Kotlin, use the safe cast operator `as?`, which returns `null` on failure:

```kotlin
// Kotlin
fun main() {
    println(getStringLength(1)) // Prints -1
}

fun getStringLength(y: Any): Int {
    val x: String? = y as? String // null if y is not `String`
    return x?.length ?: -1 // Returns -1 because x is null
}
```

### Using let()

The `let()` function is a scope function that:
- is available on any object,
- returns the result of the lambda expression,
- is often used together with the safe-call operator `?.let { ... }` to handle nullable values in a concise way.

Example with a nullable variable:

```kotlin
var newString: String? = "Kotlin from Android"
newString?.let { println("The string value is: $it") }
newString = null
newString?.let { println("The string value is: $it") } // will not run
```

The lambda inside `?.let { ... }` is executed only when `newString` is not `null`. Inside the lambda, `it` has a non-null type.

### Using also()

The `also()` function is another scope function that:
- is available on any object,
- returns the original receiver object,
- is commonly used for logging or side effects in call chains.

Example with a nullable value and logging:

```kotlin
var c = "Hello"

var newString: String? = "Kotlin from Android"
newString = newString
    ?.also { println("Logging the value: $it") } // runs only if not null
    ?.also { c = it }                            // here it is non-null
```

Be careful with chaining: in an expression like

```kotlin
newString?.let { c = it }.also { println("Logging the value: $it") }
```

`also` operates on the result of `let` (which may be `Unit` or `null`), not on `newString`, and will be called regardless of whether `newString` is `null`. This can lead to `it` being `null` or not what you expect.

Also see [[c-kotlin]].

## Дополнительные вопросы (RU)

- В чем ключевые отличия подхода к null-безопасности в Kotlin по сравнению с Java?
- Когда на практике вы будете использовать механизмы null-безопасности Kotlin?
- Каковы распространенные ошибки и подводные камни при работе с nullability в Kotlin?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Nullability in Java and Kotlin](https://kotlinlang.org/docs/java-to-kotlin-nullability-guide.html)
- [Null safety](https://kotlinlang.org/docs/null-safety.html)
- [Null safety tutorial](https://kotlinlang.org/docs/tutorials/kotlin-for-py/null-safety.html)

## References
- [Nullability in Java and Kotlin](https://kotlinlang.org/docs/java-to-kotlin-nullability-guide.html)
- [Null safety](https://kotlinlang.org/docs/null-safety.html)
- [Null safety tutorial](https://kotlinlang.org/docs/tutorials/kotlin-for-py/null-safety.html)

## Связанные вопросы (RU)

- [[q-kotlin-lateinit--kotlin--medium]]
- [[q-kotlin-type-system--kotlin--medium]]

## Related Questions
- [[q-kotlin-lateinit--kotlin--medium]]
- [[q-kotlin-type-system--kotlin--medium]]

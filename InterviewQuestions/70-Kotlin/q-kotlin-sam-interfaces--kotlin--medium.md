---
id: kotlin-025
title: "Kotlin SAM Interfaces / SAM интерфейсы в Kotlin"
aliases: ["Kotlin SAM Interfaces, SAM интерфейсы в Kotlin"]

# Classification
topic: kotlin
subtopics: [functional-programming, interfaces, lambdas]
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
related: [q-data-sealed-usage--programming-languages--medium, q-nothing-instances--programming-languages--easy, q-semaphore-rate-limiting--kotlin--medium]

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [difficulty/medium, functional-programming, interfaces, kotlin, lambdas, sam]
date created: Sunday, October 12th 2025, 12:27:47 pm
date modified: Saturday, November 1st 2025, 5:43:24 pm
---

# Question (EN)
> What do you know about functional (SAM) interfaces in Kotlin?
# Вопрос (RU)
> Что вы знаете о функциональных (SAM) интерфейсах в Kotlin?

---

## Answer (EN)

An interface with only one abstract method is called a **functional interface**, or a **Single Abstract Method (SAM) interface**. The functional interface can have several non-abstract members but only one abstract member.

To declare a functional interface in Kotlin, use the `fun` modifier.

```kotlin
fun interface KRunnable {
   fun invoke()
}
```

### SAM Conversions

For functional interfaces, you can use SAM conversions that help make your code more concise and readable by using lambda expressions.

Instead of creating a class that implements a functional interface manually, you can use a lambda expression. With a SAM conversion, Kotlin can convert any lambda expression whose signature matches the signature of the interface's single method into the code, which dynamically instantiates the interface implementation.

For example, consider the following Kotlin functional interface:

```kotlin
fun interface IntPredicate {
   fun accept(i: Int): Boolean
}
```

If you don't use a SAM conversion, you will need to write code like this:

```kotlin
// Creating an instance of a class
val isEven = object : IntPredicate {
   override fun accept(i: Int): Boolean {
       return i % 2 == 0
   }
}
```

By leveraging Kotlin's SAM conversion, you can write the following equivalent code instead:

```kotlin
// Creating an instance using lambda
val isEven = IntPredicate { it % 2 == 0 }
```

A short lambda expression replaces all the unnecessary code:

```kotlin
fun interface IntPredicate {
   fun accept(i: Int): Boolean
}

val isEven = IntPredicate { it % 2 == 0 }

fun main() {
   println("Is 7 even? - ${isEven.accept(7)}")
}
```

### @FunctionalInterface Annotation

`@FunctionalInterface` Annotation:
- This annotation is not mandatory but helps indicate that an interface is intended to be a functional interface;
- It provides compile-time checking to ensure the interface adheres to the single abstract method constraint.

```kotlin
@FunctionalInterface
interface MyFunctionalInterface {
    fun performAction(name: String)
}
```

### Functional Interfaces with Default Methods

Functional interfaces can have default methods, which provide additional functionality without breaking the single abstract method rule:

```kotlin
@FunctionalInterface
interface Worker {
    fun work(task: String)

    // Default method
    fun rest() {
        println("Taking a break")
    }
}

fun main() {
    val worker: Worker = Worker { task ->
        println("Working on $task")
    }

    worker.work("Project")
    worker.rest() // Calling the default method
}
```

### Summary

Functional interfaces in Kotlin are interfaces with a single abstract method, designed to facilitate functional programming and enhance Java interoperability. Key features include:
- Single Abstract Method (SAM): Ensures the interface has only one abstract method;
- `@FunctionalInterface` Annotation: Optional annotation to enforce SAM compliance;
- SAM Conversion: Allows lambdas to be used where functional interfaces are expected;
- Interoperability with Java: Enables seamless use of Java functional interfaces in Kotlin;
- Default Methods: Provides additional functionality without breaking the single abstract method constraint;
- Higher-Order Functions: Supports passing functional interfaces as parameters for flexible and reusable code.

## Ответ (RU)

Интерфейс только с одним абстрактным методом называется **функциональным интерфейсом**, или **Single Abstract Method (SAM) интерфейсом**. Функциональный интерфейс может иметь несколько неабстрактных членов, но только один абстрактный член.

Чтобы объявить функциональный интерфейс в Kotlin, используйте модификатор `fun`.

```kotlin
fun interface KRunnable {
   fun invoke()
}
```

### SAM Конверсии

Для функциональных интерфейсов вы можете использовать SAM конверсии, которые помогают сделать ваш код более кратким и читаемым, используя лямбда-выражения.

Вместо создания класса, который вручную реализует функциональный интерфейс, вы можете использовать лямбда-выражение. С помощью SAM конверсии Kotlin может конвертировать любое лямбда-выражение, сигнатура которого соответствует сигнатуре единственного метода интерфейса, в код, который динамически создает экземпляр реализации интерфейса.

Например, рассмотрим следующий функциональный интерфейс Kotlin:

```kotlin
fun interface IntPredicate {
   fun accept(i: Int): Boolean
}
```

Если вы не используете SAM конверсию, вам нужно будет написать такой код:

```kotlin
// Создание экземпляра класса
val isEven = object : IntPredicate {
   override fun accept(i: Int): Boolean {
       return i % 2 == 0
   }
}
```

Используя SAM конверсию Kotlin, вы можете написать следующий эквивалентный код:

```kotlin
// Создание экземпляра используя лямбду
val isEven = IntPredicate { it % 2 == 0 }
```

Короткое лямбда-выражение заменяет весь ненужный код:

```kotlin
fun interface IntPredicate {
   fun accept(i: Int): Boolean
}

val isEven = IntPredicate { it % 2 == 0 }

fun main() {
   println("Is 7 even? - ${isEven.accept(7)}")
}
```

### Аннотация @FunctionalInterface

Аннотация `@FunctionalInterface`:
- Эта аннотация не обязательна, но помогает указать, что интерфейс предназначен быть функциональным интерфейсом;
- Она обеспечивает проверку во время компиляции, чтобы убедиться, что интерфейс соответствует ограничению единственного абстрактного метода.

```kotlin
@FunctionalInterface
interface MyFunctionalInterface {
    fun performAction(name: String)
}
```

### Функциональные Интерфейсы С Методами По Умолчанию

Функциональные интерфейсы могут иметь методы по умолчанию, которые предоставляют дополнительную функциональность без нарушения правила единственного абстрактного метода:

```kotlin
@FunctionalInterface
interface Worker {
    fun work(task: String)

    // Метод по умолчанию
    fun rest() {
        println("Taking a break")
    }
}

fun main() {
    val worker: Worker = Worker { task ->
        println("Working on $task")
    }

    worker.work("Project")
    worker.rest() // Вызов метода по умолчанию
}
```

### Резюме

Функциональные интерфейсы в Kotlin — это интерфейсы с одним абстрактным методом, предназначенные для облегчения функционального программирования и улучшения совместимости с Java. Ключевые особенности включают:
- Single Abstract Method (SAM): Гарантирует, что интерфейс имеет только один абстрактный метод;
- Аннотация `@FunctionalInterface`: Опциональная аннотация для обеспечения соответствия SAM;
- SAM конверсия: Позволяет использовать лямбды там, где ожидаются функциональные интерфейсы;
- Совместимость с Java: Обеспечивает бесшовное использование функциональных интерфейсов Java в Kotlin;
- Методы по умолчанию: Предоставляет дополнительную функциональность без нарушения ограничения единственного абстрактного метода;
- Функции высшего порядка: Поддерживает передачу функциональных интерфейсов в качестве параметров для гибкого и переиспользуемого кода.

---

## References
- [Functional (SAM) interfaces](https://kotlinlang.org/docs/fun-interfaces.html)
- [Everything you want to know about Functional interfaces in Kotlin](https://www.droidcon.com/2024/05/31/everything-you-want-to-know-about-functional-interfaces-in-kotlin/)
- [SAM Conversions in Kotlin](https://www.baeldung.com/kotlin/sam-conversions)

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Related Questions

### Related (Medium)
- [[q-functional-interfaces-vs-type-aliases--kotlin--medium]] - Functional Interfaces
- [[q-kotlin-fold-reduce--kotlin--medium]] - Collections
- [[q-kotlin-higher-order-functions--kotlin--medium]] - Higher Order Functions
- [[q-kotlin-lambda-expressions--kotlin--medium]] - Lambda Expressions

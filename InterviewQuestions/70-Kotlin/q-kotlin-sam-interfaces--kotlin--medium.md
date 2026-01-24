---
id: kotlin-025
title: Kotlin SAM Interfaces / SAM интерфейсы в Kotlin
aliases:
- Kotlin SAM Interfaces
- SAM интерфейсы в Kotlin
topic: kotlin
subtopics:
- functions
- interfaces
- lambdas
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
- q-semaphore-rate-limiting--kotlin--medium
created: 2025-10-05
updated: 2025-11-09
tags:
- difficulty/medium
- functional-programming
- interfaces
- kotlin
- lambdas
- sam
anki_cards:
- slug: kotlin-025-0-en
  language: en
  anki_id: 1768326291481
  synced_at: '2026-01-23T17:03:51.511551'
- slug: kotlin-025-0-ru
  language: ru
  anki_id: 1768326291505
  synced_at: '2026-01-23T17:03:51.513025'
---
# Вопрос (RU)
> Что вы знаете о функциональных (SAM) интерфейсах в Kotlin?

---

# Question (EN)
> What do you know about functional (SAM) interfaces in Kotlin?

## Ответ (RU)

Интерфейс только с одним абстрактным методом называется **функциональным интерфейсом**, или **Single Abstract Method (SAM) интерфейсом**. Функциональный интерфейс может иметь несколько неабстрактных членов, но только один абстрактный член.

В Kotlin собственные функциональные интерфейсы объявляются с помощью модификатора `fun`.

```kotlin
fun interface KRunnable {
   fun invoke()
}
```

### SAM Конверсии

Для функциональных интерфейсов вы можете использовать SAM-конверсии, которые помогают сделать ваш код более кратким и читаемым, используя лямбда-выражения.

Вместо создания класса, который вручную реализует функциональный интерфейс, вы можете использовать лямбда-выражение. С помощью SAM-конверсии Kotlin может конвертировать лямбда-выражение, сигнатура которого соответствует сигнатуре единственного абстрактного метода интерфейса, в экземпляр реализации этого интерфейса.

Например, рассмотрим следующий функциональный интерфейс Kotlin:

```kotlin
fun interface IntPredicate {
   fun accept(i: Int): Boolean
}
```

Без SAM-конверсии вам нужно было бы написать такой код:

```kotlin
// Создание экземпляра анонимного класса
val isEven = object : IntPredicate {
   override fun accept(i: Int): Boolean {
       return i % 2 == 0
   }
}
```

Используя SAM-конверсию Kotlin, вы можете написать следующий эквивалентный код:

```kotlin
// Создание экземпляра, используя лямбду
val isEven = IntPredicate { it % 2 == 0 }
```

Короткое лямбда-выражение заменяет весь лишний код:

```kotlin
fun interface IntPredicate {
   fun accept(i: Int): Boolean
}

val isEven = IntPredicate { it % 2 == 0 }

fun main() {
   println("Is 7 even? - ${isEven.accept(7)}")
}
```

Обратите внимание:
- SAM-конверсии в Kotlin поддерживаются для `fun interface` и для Java-функциональных интерфейсов (интерфейсы с одним абстрактным методом),
- но не для произвольных Kotlin-интерфейсов, у которых просто случайно один абстрактный метод (без `fun interface`).

### Аннотация `@FunctionalInterface`

Аннотация `@FunctionalInterface` является Java-аннотацией:
- Она не обязательна, но в Java помогает указать, что интерфейс предназначен быть функциональным интерфейсом;
- Она обеспечивает проверку во время компиляции в Java, чтобы убедиться, что интерфейс соответствует ограничению единственного абстрактного метода;
- В контексте Kotlin она обычно используется на Java-коде или Java-интерфейсах, с которыми вы интероперируете; для Kotlin-функциональных интерфейсов следует использовать ключевое слово `fun`, а не полагаться на `@FunctionalInterface`.

```java
@FunctionalInterface
public interface MyFunctionalInterface {
    void performAction(String name);
}
```

Такой интерфейс можно использовать из Kotlin как функциональный (SAM) интерфейс:

```kotlin
val action = MyFunctionalInterface { name -> println("Hello, $name") }
```

### Функциональные Интерфейсы С Методами По Умолчанию

Функциональные интерфейсы могут иметь методы по умолчанию, которые предоставляют дополнительную функциональность без нарушения правила единственного абстрактного метода:

```kotlin
fun interface Worker {
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

Функциональные интерфейсы в Kotlin — это интерфейсы с одним абстрактным методом, объявляемые через `fun interface`, предназначенные для облегчения функционального программирования и улучшения совместимости с Java. Ключевые моменты:
- Single Abstract Method (SAM): Интерфейс имеет только один абстрактный метод; остальные члены могут быть конкретными/по умолчанию;
- `fun interface`: Канонический способ объявления функционального интерфейса в Kotlin;
- SAM-конверсия: Позволяет использовать лямбды там, где ожидаются `fun interface` или Java-функциональные интерфейсы;
- Совместимость с Java: Позволяет бесшовно использовать Java-функциональные интерфейсы (включая помеченные `@FunctionalInterface`) в Kotlin;
- Методы по умолчанию: Разрешены и не нарушают ограничение единственного абстрактного метода;
- Функции высшего порядка и лямбды: Часто функциональные интерфейсы конкурируют с типами функций; выбор зависит от требований к читаемости, бинарной совместимости и Java-интеропу.

## Дополнительные Вопросы (RU)

- Каковы ключевые отличия функциональных интерфейсов в Kotlin от Java?
- Когда вы бы выбрали `fun interface` вместо типа функции на практике?
- Какие распространенные ошибки и подводные камни при использовании SAM-интерфейсов в Kotlin?

## Ссылки (RU)

- [Functional (SAM) interfaces](https://kotlinlang.org/docs/fun-interfaces.html)
- [Everything you want to know about Functional interfaces in Kotlin](https://www.droidcon.com/2024/05/31/everything-you-want-to-know-about-functional-interfaces-in-kotlin/)
- [SAM Conversions in Kotlin](https://www.baeldung.com/kotlin/sam-conversions)
- [[c-kotlin]]

## Связанные Вопросы (RU)

### Связанные (Medium)
- [[q-functional-interfaces-vs-type-aliases--kotlin--medium]] — Функциональные интерфейсы vs typealias
- [[q-kotlin-fold-reduce--kotlin--medium]] — Операции fold/reduce в коллекциях
- [[q-kotlin-higher-order-functions--kotlin--medium]] — Функции высшего порядка в Kotlin
- [[q-kotlin-lambda-expressions--kotlin--medium]] — Лямбда-выражения в Kotlin

---

## Answer (EN)

An interface with only one abstract method is called a **functional interface**, or a **Single Abstract Method (SAM) interface**. A functional interface can have several non-abstract members but only one abstract member.

In Kotlin, dedicated functional interfaces are declared using the `fun` modifier.

```kotlin
fun interface KRunnable {
   fun invoke()
}
```

### SAM Conversions

For functional interfaces, you can use SAM conversions that help make your code more concise and readable by using lambda expressions.

Instead of manually creating a class that implements a functional interface, you can use a lambda expression. With SAM conversion, Kotlin can convert a lambda expression whose signature matches the single abstract method of the interface into an instance of that interface.

For example, consider the following Kotlin functional interface:

```kotlin
fun interface IntPredicate {
   fun accept(i: Int): Boolean
}
```

Without SAM conversion, you would need to write code like this:

```kotlin
// Creating an instance of an anonymous class
val isEven = object : IntPredicate {
   override fun accept(i: Int): Boolean {
       return i % 2 == 0
   }
}
```

By leveraging Kotlin's SAM conversion, you can write the following equivalent code instead:

```kotlin
// Creating an instance using a lambda
val isEven = IntPredicate { it % 2 == 0 }
```

A short lambda expression replaces all the verbose boilerplate:

```kotlin
fun interface IntPredicate {
   fun accept(i: Int): Boolean
}

val isEven = IntPredicate { it % 2 == 0 }

fun main() {
   println("Is 7 even? - ${isEven.accept(7)}")
}
```

Note:
- SAM conversions in Kotlin are supported for `fun interface` and for Java functional interfaces (single abstract method interfaces),
- but not for arbitrary Kotlin interfaces that merely happen to have a single abstract method without being declared as `fun interface`.

### `@FunctionalInterface` Annotation

The `@FunctionalInterface` annotation is a Java annotation:
- It is not mandatory, but in Java it helps indicate that an interface is intended to be a functional interface;
- It provides compile-time checking to ensure the interface adheres to the single abstract method constraint;
- In Kotlin, you typically see it on Java interfaces you interoperate with; for Kotlin functional interfaces you should rely on the `fun` modifier rather than `@FunctionalInterface`.

```java
@FunctionalInterface
public interface MyFunctionalInterface {
    void performAction(String name);
}
```

Such an interface can be used from Kotlin as a functional (SAM) interface:

```kotlin
val action = MyFunctionalInterface { name -> println("Hello, $name") }
```

### Functional Interfaces with Default Methods

Functional interfaces can have default methods, which provide additional functionality without breaking the single abstract method rule:

```kotlin
fun interface Worker {
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

Functional interfaces in Kotlin are interfaces with a single abstract method, declared via `fun interface`, designed to facilitate functional programming and enhance Java interoperability. Key points include:
- Single Abstract Method (SAM): The interface has only one abstract method; other members may be concrete/default;
- `fun interface`: The canonical way to declare a functional interface in Kotlin;
- SAM Conversion: Allows lambdas to be used where `fun interface` or Java functional interfaces are expected;
- Interoperability with Java: Enables seamless use of Java functional interfaces (including those annotated with `@FunctionalInterface`) from Kotlin;
- Default Methods: Allowed and do not break the single abstract method constraint;
- Higher-Order Functions and Lambdas: Functional interfaces often compete with plain function types; choose based on readability, binary stability, and Java interop needs.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Functional (SAM) interfaces](https://kotlinlang.org/docs/fun-interfaces.html)
- [Everything you want to know about Functional interfaces in Kotlin](https://www.droidcon.com/2024/05/31/everything-you-want-to-know-about-functional-interfaces-in-kotlin/)
- [SAM Conversions in Kotlin](https://www.baeldung.com/kotlin/sam-conversions)

## Related Questions

### Related (Medium)
- [[q-functional-interfaces-vs-type-aliases--kotlin--medium]] - Functional Interfaces
- [[q-kotlin-fold-reduce--kotlin--medium]] - Collections
- [[q-kotlin-higher-order-functions--kotlin--medium]] - Higher Order Functions
- [[q-kotlin-lambda-expressions--kotlin--medium]] - Lambda Expressions

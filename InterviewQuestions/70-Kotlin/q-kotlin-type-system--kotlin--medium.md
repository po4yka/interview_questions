---
id: kotlin-028
title: "Kotlin Type System (Any, Nothing, Unit) / Система типов Kotlin (Any, Nothing, Unit)"
aliases: ["Kotlin Type System (Any, Nothing, Unit)", "Система типов Kotlin (Any, Nothing, Unit)"]

# Classification
topic: kotlin
subtopics: [type-system]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: "https://github.com/Kirchhoff-/Android-Interview-Questions"
source_note: Kirchhoff Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-kotlin, q-data-class-detailed--kotlin--medium]

# Timestamps
created: 2025-10-05
updated: 2025-11-09

tags: [difficulty/medium, kotlin, type-system, types]
date created: Sunday, October 12th 2025, 12:27:47 pm
date modified: Tuesday, November 25th 2025, 8:53:50 pm
---
# Вопрос (RU)
> Что вы знаете о типах Any, Nothing, Unit в Kotlin?

---

# Question (EN)
> What do you know about Any, Nothing, Unit types in Kotlin?

## Ответ (RU)

### Any

`Any` — это корень иерархии классов Kotlin для всех not-null типов. Все non-nullable типы неявно наследуются от `Any`. `Any` сам по себе не может содержать значение `null`; для хранения значения `null` используется `Any?`. Тип `Any?` является суперклассом для всех типов, включая `null`.

Компилятор Kotlin обрабатывает `kotlin.Any` и `java.lang.Object` как разные типы, но на JVM во время выполнения они представлены одним и тем же классом `java.lang.Object`. У `Any` определены только `equals()`, `hashCode()` и `toString()`, остальные методы Java `Object` доступны через интероп или расширения.

### Nothing

`Nothing` не имеет экземпляров. Его используют для представления "значения, которое никогда не существует": например, если функция имеет тип возврата `Nothing`, это означает, что она никогда не возвращается (всегда выбрасывает исключение или бесконечно блокируется / зацикливается).

`Nothing` является нижним типом (bottom type) и подтипом любого другого типа. Это позволяет использовать его там, где ожидается значение любого типа.

```kotlin
fun fail(message: String): Nothing {
    throw IllegalStateException(message)
}

val address = employee.address ?: fail("${employee.name} has no address defined")
println(address)

// > java.lang.IllegalStateException: John has no address defined
```

### Unit

В Java, если мы хотим, чтобы функция ничего не возвращала, мы используем `void`. В Kotlin для этого используется `Unit`.

Основные характеристики `Unit` по сравнению с `void` в Java:
- `Unit` является полноценным типом и поэтому может использоваться как аргумент типа.
- Существует только одно значение этого типа — `Unit`.
- Это значение возвращается неявно: для функции с возвращаемым типом `Unit` оператор `return` не требуется (кроме случаев явного `return Unit`).

## Дополнительные Вопросы (RU)

- В чем ключевые отличия по сравнению с Java?
- Когда вы бы использовали эти типы на практике?
- Какие распространенные ошибки следует избегать?

## Ссылки (RU)
- [[c-kotlin]]
- [Kotlin Basics: Types Any, Unit and Nothing](https://itnext.io/kotlin-basics-types-any-unit-and-nothing-674cc858035)
- [Kotlin's Nothing Type](https://proandroiddev.com/kotlins-nothing-type-946de7d464fb)
- [Kotlin's Nothing: Its usefulness in Generics](https://blog.kotlin-academy.com/kotlins-nothing-its-usefulness-in-generics-5076a6a457f7)
- [Any API Documentation](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin/-any/)
- [Nothing API Documentation](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin/-nothing.html)
- [Unit API Documentation](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin/-unit/)

---

## Answer (EN)

### Any

`Any` is the root of the Kotlin class hierarchy for all non-null types. All non-nullable types implicitly inherit from `Any`. `Any` itself cannot hold the `null` value; to hold a `null` value you use `Any?`. The type `Any?` is the supertype of all types including `null`.

The Kotlin compiler treats `kotlin.Any` and `java.lang.Object` as different types, but on the JVM at runtime they are represented by the same `java.lang.Object` class. `Any` defines only `equals()`, `hashCode()`, and `toString()`; other `Object` methods are accessed via interop or extensions.

### Nothing

`Nothing` has no instances. You use `Nothing` to represent "a value that never exists": for example, if a function has the return type `Nothing`, it means that it never returns (it always throws an exception or never completes).

`Nothing` is the bottom type and a subtype of every other type. This allows it to be used in places where a value of any type is expected.

```kotlin
fun fail(message: String): Nothing {
    throw IllegalStateException(message)
}

val address = employee.address ?: fail("${employee.name} has no address defined")
println(address)

// > java.lang.IllegalStateException: John has no address defined
```

### Unit

In Java, if we want a function to return no value, we use `void`. In Kotlin, the equivalent is `Unit`.

The main characteristics of `Unit` compared to Java's `void` are:
- `Unit` is a proper type and therefore can be used as a type argument.
- Only one value of this type exists — `Unit`.
- This value is returned implicitly: for a function with the return type `Unit`, there is no need for a `return` statement (except for an explicit `return Unit` if desired).

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Kotlin Basics: Types Any, Unit and Nothing](https://itnext.io/kotlin-basics-types-any-unit-and-nothing-674cc858035)
- [Kotlin's Nothing Type](https://proandroiddev.com/kotlins-nothing-type-946de7d464fb)
- [Kotlin's Nothing: Its usefulness in Generics](https://blog.kotlin-academy.com/kotlins-nothing-its-usefulness-in-generics-5076a6a457f7)
- [Any API Documentation](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin/-any/)
- [Nothing API Documentation](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin/-nothing.html)
- [Unit API Documentation](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin/-unit/)

## Related Questions
- [[q-kotlin-null-safety--kotlin--medium]]
- [[q-kotlin-generics--kotlin--hard]]

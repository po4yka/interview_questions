---
id: 20251005-222657
title: "Kotlin Type System (Any, Nothing, Unit) / Система типов Kotlin (Any, Nothing, Unit)"
aliases: []

# Classification
topic: kotlin
subtopics: [types, any, nothing, unit, type-system]
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

tags: [kotlin, types, any, nothing, unit, type-system, difficulty/medium]
---
## Question (EN)
> What do you know about Any, Nothing, Unit types in Kotlin?
## Вопрос (RU)
> Что вы знаете о типах Any, Nothing, Unit в Kotlin?

---

## Answer (EN)

### Any

`Any` is the root of the Kotlin class hierarchy. `Any` is the super type of all non-nullable types. `Any` can't hold the `null` value, for holding `null` value you can use `Any?`. Kotlin compiler treats `kotlin.Any` and `java.lang.Object` as two different types, but at runtime they are represented with the same `java.lang.Object` class.

### Nothing

`Nothing` has no instances. You can use Nothing to represent "a value that never exists": for example, if a function has the return type of Nothing, it means that it never returns (always throws an exception). `Nothing` implicitly extends any object that exists.

```kotlin
fun fail(message: String): Nothing {
    throw IllegalStateException(message)
}

val address = employee.address ?: fail("${employee.name} has no address defined")
println(address)

// > java.lang.IllegalStateException: John has no address defined
```

### Unit

In Java if we want that a function does return nothing we use `void`, `Unit` is the equivalent in Kotlin. The main characteristics of `Unit` against Java's `void` are:
- `Unit` is a type and therefore can be used as a type argument.
- Only one value of this type exists.
- It is returned implicitly. No need of a `return` statement.

## Ответ (RU)

### Any

`Any` — это корень иерархии классов Kotlin. `Any` является супертипом всех non-nullable типов. `Any` не может содержать значение `null`, для хранения значения `null` вы можете использовать `Any?`. Компилятор Kotlin обрабатывает `kotlin.Any` и `java.lang.Object` как два разных типа, но во время выполнения они представлены одним и тем же классом `java.lang.Object`.

### Nothing

`Nothing` не имеет экземпляров. Вы можете использовать Nothing для представления "значения, которое никогда не существует": например, если функция имеет тип возврата Nothing, это означает, что она никогда не возвращается (всегда выбрасывает исключение). `Nothing` неявно расширяет любой существующий объект.

```kotlin
fun fail(message: String): Nothing {
    throw IllegalStateException(message)
}

val address = employee.address ?: fail("${employee.name} has no address defined")
println(address)

// > java.lang.IllegalStateException: John has no address defined
```

### Unit

В Java, если мы хотим, чтобы функция ничего не возвращала, мы используем `void`, `Unit` — это эквивалент в Kotlin. Основные характеристики `Unit` по сравнению с `void` в Java:
- `Unit` является типом и поэтому может использоваться как аргумент типа.
- Существует только одно значение этого типа.
- Оно возвращается неявно. Не требуется оператор `return`.

---

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

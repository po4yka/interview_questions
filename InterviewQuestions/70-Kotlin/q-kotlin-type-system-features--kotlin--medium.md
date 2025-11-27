---
id: kotlin-141
title: "Kotlin Type System Features / Возможности системы типов Kotlin"
aliases: [Null Safety, Type Safety, Type System]
topic: kotlin
subtopics: [null-safety, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-kotlin-features, q-kotlin-coroutines-introduction--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/medium, kotlin, null-safety, type-inference, type-system]
date created: Friday, October 31st 2025, 6:28:53 pm
date modified: Tuesday, November 25th 2025, 8:53:50 pm
---
# Вопрос (RU)
> Какие особенности системы типов в Kotlin ты знаешь?

# Question (EN)
> What Kotlin type system features do you know?

## Ответ (RU)

Ниже перечислены ключевые особенности системы типов Kotlin (см. также [[c-kotlin]], [[c-kotlin-features]]). Некоторые из них относятся непосредственно к системе типов, другие тесно с ней связаны и опираются на неё:

### 1. Null Safety (Безопасность null)
По умолчанию переменные не могут содержать `null`, что помогает предотвращать `NullPointerException`. Чтобы значение могло быть `null`, тип нужно явно пометить `?`:
```kotlin
var nonNull: String = "Hello"      // Не может быть null
var nullable: String? = null        // Явно допускает null
```

### 2. Коллекции: Read-only Vs Mutable
В Kotlin чётко разделены интерфейсы для только-чтения (read-only) и изменяемых коллекций. Read-only коллекции предоставляют неизменяемый интерфейс, но не всегда гарантируют структурную неизменяемость реализации.
```kotlin
val list: List<String> = listOf("a", "b")              // Интерфейс только для чтения
val mutableList: MutableList<String> = mutableListOf("a", "b")
```

### 3. Data Classes (Классы данных)
`data class` используют возможности системы типов и позволяют компилятору автоматически генерировать `equals()`, `hashCode()`, `toString()`, `componentN()` и `copy()` на основе свойств первичного конструктора:
```kotlin
data class User(val name: String, val age: Int)
```

### 4. Smart Casts (Умные Приведения типов)
После проверки с помощью `is` (и при отсутствии побочных эффектов) компилятор автоматически приводит тип внутри соответствующей ветки:
```kotlin
fun demo(x: Any) {
    if (x is String) {
        println(x.length)  // x автоматически рассматривается как String
    }
}
```

### 5. Sealed Иерархии (Закрытые Иерархии типов)
`sealed`-иерархии ограничивают набор допустимых подтипов, что упрощает исчерпывающую обработку в `when` без ветки `else` при покрытии всех вариантов:
```kotlin
sealed class Result {
    data class Success(val data: String) : Result()
    data class Error(val message: String) : Result()
}
```

### 6. Type Inference (Выведение типов)
Kotlin во многих случаях автоматически выводит тип переменных и выражений (локальное выведение типов), что уменьшает шаблонный код:
```kotlin
val x = 10        // Тип выведен как Int
val name = "John" // Тип выведен как String
```

Эти возможности (null-safety, умные приведения, sealed-иерархии, разделение коллекций, data-классы и выведение типов) делают код на Kotlin более безопасным, выразительным и компактным.

## Answer (EN)

Kotlin's type system has several powerful features. Some are core type system constructs, others are language features that build on and leverage the type system:

### 1. Null Safety
By default, variables cannot hold `null`, helping to avoid `NullPointerException`. To allow `null`, you must explicitly mark the type as nullable with `?`:
```kotlin
var nonNull: String = "Hello"      // Cannot be null
var nullable: String? = null        // Explicitly nullable
```

### 2. Collections: Read-only Vs Mutable
Kotlin clearly distinguishes between read-only collection interfaces and mutable ones. Read-only collections expose a non-mutating API but do not always guarantee structural immutability of the underlying collection.
```kotlin
val list: List<String> = listOf("a", "b")              // Read-only view
val mutableList: MutableList<String> = mutableListOf("a", "b")
```

### 3. Data Classes
`data class` leverages the type system and instructs the compiler to automatically generate `equals()`, `hashCode()`, `toString()`, `componentN()`, and `copy()` based on the primary constructor properties:
```kotlin
data class User(val name: String, val age: Int)
```

### 4. Smart Casts
After a successful `is` check (and when the value cannot change in between), the compiler automatically smart-casts the variable within that scope:
```kotlin
fun demo(x: Any) {
    if (x is String) {
        println(x.length)  // x is smart-cast to String
    }
}
```

### 5. Sealed Hierarchies
`sealed` hierarchies define restricted subtype sets, making exhaustive `when` expressions easier and safer (no `else` needed when all variants are covered):
```kotlin
sealed class Result {
    data class Success(val data: String) : Result()
    data class Error(val message: String) : Result()
}
```

### 6. Type Inference
Kotlin can infer types from context (primarily locally), reducing boilerplate while keeping static type safety:
```kotlin
val x = 10        // Inferred as Int
val name = "John" // Inferred as String
```

These features (null safety, smart casts, sealed hierarchies, collection APIs, data classes, and type inference) make Kotlin code safer, more concise, and more expressive.

## Дополнительные Вопросы (RU)

- В чем ключевые отличия системы типов Kotlin от Java?
- Когда на практике особенно важно использовать эти возможности системы типов Kotlin (null-safety, умные приведения, sealed-иерархии, разделение коллекций)?
- Каковы распространенные ошибки и подводные камни при использовании этих особенностей, и как их избежать?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-kotlin-coroutines-introduction--kotlin--medium]]

## Follow-ups

- What are the key differences between Kotlin's type system and Java's?
- When are these Kotlin type system features (null safety, smart casts, sealed hierarchies, read-only vs mutable collections) particularly important in practice?
- What are common mistakes and pitfalls when using these features, and how can they be avoided?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-kotlin-coroutines-introduction--kotlin--medium]]

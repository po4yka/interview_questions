---
id: kotlin-002
title: "Equality Operators == vs === / Операторы равенства == vs ==="
aliases: []

# Classification
topic: kotlin
subtopics: [comparison, equality, operators]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository - Kotlin Batch 2

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-kotlin-favorite-features--programming-languages--easy, q-kotlin-object-companion-object--programming-languages--easy, q-test-dispatcher-types--kotlin--medium]

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [comparison, difficulty/easy, equality, kotlin, operators]
date created: Sunday, October 12th 2025, 12:27:46 pm
date modified: Saturday, November 1st 2025, 5:43:26 pm
---

# Question (EN)
> What is the difference between == and === in Kotlin?
# Вопрос (RU)
> В чем разница между == и === в Kotlin?

---

## Answer (EN)

Kotlin has two types of equality: **structural** and **referential**.

### == (Structural Equality)

Checks if objects have **equal values**. Equivalent to `equals()` method in Java.

```kotlin
val a = "hello"
val b = "hello"
println(a == b)  // true - same content

val list1 = listOf(1, 2, 3)
val list2 = listOf(1, 2, 3)
println(list1 == list2)  // true - same content
```

### === (Referential Equality)

Checks if two references point to the **same object**. Equivalent to `==` operator in Java.

```kotlin
val a = "hello"
val b = "hello"
println(a === b)  // true (string pool optimization)

val list1 = mutableListOf(1, 2, 3)
val list2 = mutableListOf(1, 2, 3)
println(list1 === list2)  // false - different objects
println(list1 === list1)  // true - same object
```

### Summary Table

| Operator | Purpose | Java Equivalent | Null Safe |
|----------|---------|-----------------|-----------|
| `==` | Structural equality (content) | `equals()` | Yes (`a?.equals(b) ?: (b === null)`) |
| `===` | Referential equality (reference) | `==` | No |

### Examples

```kotlin
data class Person(val name: String, val age: Int)

val person1 = Person("Alice", 25)
val person2 = Person("Alice", 25)
val person3 = person1

// Structural equality
println(person1 == person2)  // true - same data
println(person1 == person3)  // true - same data

// Referential equality
println(person1 === person2)  // false - different objects
println(person1 === person3)  // true - same reference
```

**English Summary**: `==` checks structural equality (equal values/content), calls `equals()`. `===` checks referential equality (same object reference). Use `==` for comparing values, `===` for checking if two variables point to the same object.

## Ответ (RU)

В Kotlin есть два типа равенства: **структурное** и **ссылочное**.

### == (Структурное равенство)

Проверяет равны ли **значения** объектов. Эквивалентно методу `equals()` в Java.

```kotlin
val a = "hello"
val b = "hello"
println(a == b)  // true - одинаковое содержимое
```

### === (Ссылочное равенство)

Проверяет указывают ли две ссылки на **один и тот же объект**. Эквивалентно оператору `==` в Java.

```kotlin
val list1 = mutableListOf(1, 2, 3)
val list2 = mutableListOf(1, 2, 3)
println(list1 === list2)  // false - разные объекты
println(list1 === list1)  // true - тот же объект
```

**Краткое содержание**: `==` проверяет структурное равенство (равные значения/содержимое), вызывает `equals()`. `===` проверяет ссылочное равенство (тот же объект). Используйте `==` для сравнения значений, `===` для проверки указывают ли переменные на один объект.

---

## References
- [Equality - Kotlin Documentation](https://kotlinlang.org/docs/reference/equality.html)

## Related Questions

### Advanced (Harder)
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-flow-operators--kotlin--medium]] - Flow

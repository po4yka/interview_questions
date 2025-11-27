---
id: lang-048
title: "Kotlin Reference Equality Operator / Оператор ссылочного равенства в Kotlin"
aliases: [Kotlin Reference Equality Operator, Оператор ссылочного равенства в Kotlin]
topic: kotlin
subtopics: [operators, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-equality, c-kotlin, q-data-class-detailed--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/easy, equality, operators, programming-languages, reference-equality, structural-equality]
date created: Friday, October 31st 2025, 6:32:17 pm
date modified: Tuesday, November 25th 2025, 8:53:50 pm
---
# Вопрос (RU)
> Какой оператор используется для проверки равенства ссылок в Kotlin?

---

# Question (EN)
> Which operator is used to check reference equality in Kotlin?

## Ответ (RU)

В Kotlin для проверки **ссылочного равенства** используется оператор **`===`** (также называемого референтным равенством). Он проверяет, указывают ли две переменные на один и тот же объект в памяти.

См. также: [[c-kotlin]], [[c-equality]]

**Сравнение: `==` vs `===`**

```kotlin
val a = "Hello"
val b = "Hello"
val c = a

// Структурное равенство (==) - проверяет содержимое (null-safe вызов equals)
a == b   // true (одинаковое содержимое)

// Референтное равенство (===) - проверяет, один ли это объект
// Важно: результат a === b не гарантирован спецификацией Kotlin и зависит от платформы/реализации
a === b  // может быть true или false

a === c  // true (c ссылается на a)

val d = String(charArrayOf('H', 'e', 'l', 'l', 'o'))
a == d   // true (одинаковое содержимое)
a === d  // false (разные объекты в памяти)
```

**С пользовательскими объектами:**
```kotlin
data class User(val name: String)

val user1 = User("John")
val user2 = User("John")
val user3 = user1

user1 == user2   // true (data class equals проверяет содержимое)
user1 === user2  // false (разные объекты)
user1 === user3  // true (одна и та же ссылка)
```

**Ключевые различия:**

| Оператор | Назначение | Null-safe |
|----------|---------|-----------|
| `==` | Структурное равенство (компилируется в null-safe вызов `equals()`) | Да |
| `===` | Референтное равенство (один объект) | Да |
| `!=` | Структурное неравенство | Да |
| `!==` | Референтное неравенство | Да |

**Kotlin vs Java:**
- Kotlin `==` ≈ Java `.equals()` (c null-safe оберткой: `a?.equals(b) ?: (b == null)`)
- Kotlin `===` ≈ Java `==`
- `==` в Kotlin является null-safe, `==` в Java для ссылочных типов проверяет ссылки и не является null-safe в том же смысле (возможен `NullPointerException` при вызове `.equals` напрямую).

## Answer (EN)

In Kotlin, the **`===` operator** is used to check **reference equality** (also called referential equality). It checks whether two variables point to the same object in memory.

See also: [[c-kotlin]], [[c-equality]]

**Comparison: `==` vs `===`**

```kotlin
val a = "Hello"
val b = "Hello"
val c = a

// Structural equality (==) - checks content (null-safe equals)
a == b   // true (same content)

// Referential equality (===) - checks if same object
// Important: the result of a === b is not guaranteed by Kotlin spec and depends on platform/implementation
a === b  // may be true or false

a === c  // true (c references a)

val d = String(charArrayOf('H', 'e', 'l', 'l', 'o'))
a == d   // true (same content)
a === d  // false (different objects in memory)
```

**With custom objects:**
```kotlin
data class User(val name: String)

val user1 = User("John")
val user2 = User("John")
val user3 = user1

user1 == user2   // true (data class equals checks content)
user1 === user2  // false (different objects)
user1 === user3  // true (same reference)
```

**Key Differences:**

| Operator | Purpose | Null-safe |
|----------|---------|-----------|
| `==` | Structural equality (compiled to a null-safe `equals()` call) | Yes |
| `===` | Referential equality (same object) | Yes |
| `!=` | Structural inequality | Yes |
| `!==` | Referential inequality | Yes |

**Kotlin vs Java:**
- Kotlin `==` ≈ Java `.equals()` (with null-safe wrapper: `a?.equals(b) ?: (b == null)`)
- Kotlin `===` ≈ Java `==`
- Kotlin's `==` is null-safe; Java's `==` for reference types checks references and using `.equals` directly can throw `NullPointerException` when the receiver is null.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия оператора `===` от оператора `==` в Java?
- В каких случаях на практике следует использовать `===`?
- Какие распространенные ошибки и подводные камни связаны с использованием `===`?

## Follow-ups

- What are the key differences between the `===` operator and Java's `==` operator?
- When would you use `===` in practice?
- What are common pitfalls to avoid when using `===`?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-data-class-detailed--kotlin--medium]]
- [[q-destructuring-declarations--kotlin--medium]]
- [[q-mutex-synchronized-coroutines--kotlin--medium]]

## Related Questions

- [[q-data-class-detailed--kotlin--medium]]
- [[q-destructuring-declarations--kotlin--medium]]
- [[q-mutex-synchronized-coroutines--kotlin--medium]]

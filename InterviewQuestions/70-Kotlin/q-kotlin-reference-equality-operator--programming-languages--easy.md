---
id: lang-048
title: "Kotlin Reference Equality Operator / Оператор ссылочного равенства в Kotlin"
aliases: [Kotlin Reference Equality Operator, Оператор ссылочного равенства в Kotlin]
topic: programming-languages
subtopics: [type-system, operators]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-data-class-detailed--kotlin--medium, q-destructuring-declarations--kotlin--medium, q-mutex-synchronized-coroutines--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags:
  - programming-languages
  - equality
  - operators
  - reference-equality
  - structural-equality
  - difficulty/easy
---
# Какой оператор используется для проверки равенства ссылок в Kotlin?

# Question (EN)
> Which operator is used to check reference equality in Kotlin?

# Вопрос (RU)
> Какой оператор используется для проверки равенства ссылок в Kotlin?

---

## Answer (EN)

In Kotlin, the **`===` operator** is used to check **reference equality** (also called referential equality). It checks whether two variables point to the same object in memory.

**Comparison: `==` vs `===`**

```kotlin
val a = "Hello"
val b = "Hello"
val c = a

// Structural equality (==) - checks content
a == b   // true (same content)

// Referential equality (===) - checks if same object
a === b  // true (string pool - same object)
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
| `==` | Structural equality (calls `equals()`) | Yes |
| `===` | Referential equality (same object) | Yes |
| `!=` | Structural inequality | Yes |
| `!==` | Referential inequality | Yes |

**Kotlin vs Java:**
- Kotlin `==` ≈ Java `.equals()`
- Kotlin `===` ≈ Java `==`
- Kotlin's `==` is null-safe, Java's `==` checks references

---

## Ответ (RU)

В Kotlin для проверки **ссылочного равенства** используется оператор **`===`** (также называемого референтным равенством). Он проверяет, указывают ли две переменные на один и тот же объект в памяти.

**Сравнение: `==` vs `===`**

```kotlin
val a = "Hello"
val b = "Hello"
val c = a

// Структурное равенство (==) - проверяет содержимое
a == b   // true (одинаковое содержимое)

// Референтное равенство (===) - проверяет, один ли это объект
a === b  // true (string pool - один объект)
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
| `==` | Структурное равенство (вызывает `equals()`) | Да |
| `===` | Референтное равенство (один объект) | Да |
| `!=` | Структурное неравенство | Да |
| `!==` | Референтное неравенство | Да |

**Kotlin vs Java:**
- Kotlin `==` ≈ Java `.equals()`
- Kotlin `===` ≈ Java `==`
- `==` в Kotlin является null-safe, `==` в Java проверяет ссылки

## Related Questions

- [[q-data-class-detailed--kotlin--medium]]
- [[q-destructuring-declarations--kotlin--medium]]
- [[q-mutex-synchronized-coroutines--kotlin--medium]]

---
tags:
  - equality
  - kotlin
  - operators
  - programming-languages
  - reference-equality
  - structural-equality
difficulty: easy
status: reviewed
---

# Какой оператор используется для проверки равенства ссылок в Kotlin?

**English**: Which operator is used to check reference equality in Kotlin?

## Answer

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

## Ответ

В Kotlin для проверки равенства ссылок используется оператор `===`. Этот оператор проверяет, ссылаются ли две переменные на один и тот же объект в памяти. В отличие от оператора `==`, который проверяет равенство значений объектов.


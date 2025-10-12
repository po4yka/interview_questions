---
tags:
  - functions
  - generics
  - kotlin
  - programming-languages
  - syntax
  - type-parameters
difficulty: easy
status: draft
---

# Какой синтаксис используется для объявления обобщенной функции в Kotlin?

# Question (EN)
> What syntax is used to declare a generic function in Kotlin?

# Вопрос (RU)
> Какой синтаксис используется для объявления обобщенной функции в Kotlin?

---

## Answer (EN)

To declare a generic function in Kotlin, use angle brackets `<T>` before the function name:

**Syntax:**
```kotlin
fun <T> functionName(parameter: T): T {
    // function body
}
```

**Examples:**
```kotlin
// Simple generic function
fun <T> identity(value: T): T {
    return value
}

// Multiple type parameters
fun <K, V> mapOf(key: K, value: V): Map<K, V> {
    return mapOf(key to value)
}

// With type constraints
fun <T : Comparable<T>> max(a: T, b: T): T {
    return if (a > b) a else b
}

// Usage
val result = identity(42)        // T inferred as Int
val name = identity("Hello")     // T inferred as String
```

**Type parameter placement:**
- Before function name: `fun <T> name()`
- Before extension receiver: `fun <T> T.extension()`

---

## Ответ (RU)

Для объявления обобщенной функции в Kotlin используется синтаксис: fun <T> functionName() { ... }


---
tags:
  - generics
  - type-parameters
  - variance
  - bounds
  - easy_kotlin
  - programming-languages
  - kotlin
  - java
difficulty: medium
---

# Какие виды дженериков есть?

**English**: What types of generics exist?

## Answer

Generics come in several forms:

### 1. Generic Classes
Classes with type parameters:
```kotlin
class Box<T>(val value: T)

val intBox = Box<Int>(42)
val stringBox = Box("Hello")
```

### 2. Generic Methods/Functions
Methods with their own type parameters:
```kotlin
fun <T> identity(value: T): T {
    return value
}

fun <T> List<T>.second(): T {
    return this[1]
}
```

### 3. Type Bounds (Constraints)

**Upper bounds** (`extends` in Java, `:` in Kotlin):
```kotlin
// Kotlin
fun <T : Number> sum(a: T, b: T): Double {
    return a.toDouble() + b.toDouble()
}

// Java
<T extends Number> double sum(T a, T b)
```

**Multiple bounds:**
```kotlin
fun <T> process(value: T)
    where T : Comparable<T>,
          T : Serializable {
    // T must implement both interfaces
}
```

### 4. Variance Annotations

**Covariance** (`out` in Kotlin, `extends` in Java):
```kotlin
interface Producer<out T> {  // Can only produce T
    fun produce(): T
}
```

**Contravariance** (`in` in Kotlin, `super` in Java):
```kotlin
interface Consumer<in T> {   // Can only consume T
    fun consume(item: T)
}
```

### 5. Star Projection (Raw Types)
```kotlin
List<*>  // Kotlin - star projection
List     // Java - raw type (deprecated)
```

**Summary:**

| Type | Purpose | Example |
|------|---------|---------|
| Generic class | Parameterized class | `Box<T>` |
| Generic method | Parameterized method | `<T> T identity(T)` |
| Upper bound | Restrict to subtype | `<T : Number>` |
| Lower bound | Java only | `<T super Integer>` |
| Covariance | Producer | `out T` |
| Contravariance | Consumer | `in T` |
| Star projection | Unknown type | `List<*>` |

## Ответ

- Обобщённые классы class Box<T> \\- Обобщённые методы <T> void print(T t) \\- Ограничения extends, super — для указания границ типов \\- Сырые типы List без параметра — deprecated


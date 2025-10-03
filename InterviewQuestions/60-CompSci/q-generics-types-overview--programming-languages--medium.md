---
id: 20251003141113
title: Types of generics / Виды дженериков
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, java, generics]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/996
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-generics

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [generics, type-parameters, variance, bounds, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What types of generics exist

# Вопрос (RU)
> Какие виды дженериков есть

---

## Answer (EN)

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

## Ответ (RU)

- Обобщённые классы class Box<T> \\- Обобщённые методы <T> void print(T t) \\- Ограничения extends, super — для указания границ типов \\- Сырые типы List без параметра — deprecated

---

## Follow-ups
- What is variance in generics?
- What are reified type parameters in Kotlin?
- How does type erasure work?

## References
- [[c-generics]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-generic-function-syntax--programming-languages--easy]]
- [[q-runtime-generic-access--programming-languages--hard]]

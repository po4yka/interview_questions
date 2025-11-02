---
id: lang-047
title: "Reference Types Criteria / Критерии типов ссылок"
aliases: [Reference Types Criteria, Критерии типов ссылок]
topic: programming-languages
subtopics: [type-design, immutability, object-model]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-programming-languages
related: [q-interface-vs-abstract-class--programming-languages--medium, q-linkedlist-arraylist-insert-behavior--programming-languages--medium, q-xml-acronym--programming-languages--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [best-practices, design, immutability, kotlin, programming-languages, reference-types, difficulty/medium]
date created: Friday, October 3rd 2025, 6:48:06 pm
date modified: Sunday, October 26th 2025, 1:37:19 pm
---

# Каким Критериям Должны Соответствовать Ссылочные Типы?

# Question (EN)
> What criteria should reference types meet?

# Вопрос (RU)
> Каким критериям должны соответствовать ссылочные типы?

---

## Answer (EN)

Reference types in Kotlin should meet the following criteria for good design:

### 1. Immutability (When Required by Architecture)

**Use immutable types when possible:**
```kotlin
// Good: Immutable data class
data class User(val name: String, val email: String)

// Less preferred: Mutable properties
data class User(var name: String, var email: String)
```

**Benefits:**
- Thread-safe by default
- Easier to reason about
- Safe to use as Map keys or in Set
- Prevents accidental modification

### 2. Nullability (`nullable` or `not-null`)

**Choose based on requirements:**
```kotlin
// Not-null when value is always present
data class User(
    val id: String,         // Always required
    val email: String       // Always required
)

// Nullable when value may be absent
data class UserProfile(
    val bio: String?,       // Optional bio
    val avatar: String?     // Optional avatar URL
)
```

### 3. Implement Core Methods (for Collections)

**Must implement if used in collections:**
```kotlin
data class Person(val name: String, val age: Int) {
    // Data classes auto-generate:
    // - equals()
    // - hashCode()
    // - toString()
}

// Manual implementation for custom classes
class CustomType(val value: Int) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is CustomType) return false
        return value == other.value
    }

    override fun hashCode(): Int = value.hashCode()

    override fun toString(): String = "CustomType(value=$value)"
}
```

**Why it matters:**
```kotlin
val set = setOf(person1, person2)  // Needs equals/hashCode
val map = mapOf(person to "data")   // Needs equals/hashCode
println(person)                     // Needs toString
```

### 4. Lightweight (If Frequently Copied)

**Keep types small when copying is common:**
```kotlin
// Good: Small, focused
data class Point(val x: Int, val y: Int)

// Less optimal if frequently copied
data class HeavyObject(
    val largeArray: IntArray,
    val bigMap: Map<String, String>,
    val complexData: List<ComplexType>
)
```

**Consider:**
- Avoid large collections in frequently-copied types
- Use references to heavy data instead of embedding
- Profile if performance is critical

### 5. Final or Sealed (If Behavior is Fixed)

**Prefer `final` (default) or `sealed`:**
```kotlin
// Default: final class
data class User(val name: String)  // Cannot be inherited

// Sealed: restricted hierarchy
sealed class Result<out T>
data class Success<T>(val data: T) : Result<T>()
data class Error(val message: String) : Result<Nothing>()

// Open only when inheritance is intended
open class BaseEntity {
    open fun validate(): Boolean = true
}
```

**Benefits:**
- Prevents unexpected subclassing
- Enables exhaustive `when` with sealed classes
- Compiler optimizations

### Summary Checklist

| Criterion | Guideline | Reason |
|-----------|-----------|--------|
| **Immutability** | Prefer `val` over `var` | Thread-safety, predictability |
| **Nullability** | Explicit nullable vs not-null | Type safety, clear intent |
| **equals/hashCode** | Implement for collection use | Correct Set/Map behavior |
| **toString** | Provide readable representation | Debugging, logging |
| **Size** | Keep lightweight if copied often | Performance |
| **Inheritance** | Prefer final/sealed | Prevent unwanted subclassing |

---

## Ответ (RU)

Ссылочные типы в Kotlin: неизменяемые, если это требуется по архитектуре; nullable или not-null — в зависимости от требований; должны реализовывать equals, hashCode и toString особенно если используются в коллекциях; быть легковесными если часто копируются; желательно final или sealed если поведение фиксировано

## Related Questions

- [[q-xml-acronym--programming-languages--easy]]
- [[q-interface-vs-abstract-class--programming-languages--medium]]
- [[q-linkedlist-arraylist-insert-behavior--programming-languages--medium]]

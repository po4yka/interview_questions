---
id: 20251003141008
title: Data and sealed classes combination / Комбинация data и sealed классов
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, oop]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/494
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-data-classes
  - c-kotlin-sealed-classes

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, data-class, sealed-class, type-safety, when-expressions, oop, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> Tell me about data classes and sealed classes

# Вопрос (RU)
> Расскажи data классы и sealed классы

---

## Answer (EN)

### Data Classes

Data classes are designed for **storing data** and automatically generate useful methods:
- `equals()` - value-based equality
- `hashCode()` - consistent hashing
- `toString()` - readable string representation
- `copy()` - create modified copies

```kotlin
data class User(val name: String, val age: Int)

val user1 = User("John", 30)
val user2 = user1.copy(age = 31)
```

### Sealed Classes

Sealed classes represent **restricted inheritance hierarchies** where all possible subclasses are known at compile time:

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val error: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}
```

### Combining Both

Together, they create **type-safe and easily manageable data structures**, especially for `when` expressions:

```kotlin
fun handleResult(result: Result<String>) = when (result) {
    is Result.Success -> println("Data: ${result.data}")
    is Result.Error -> println("Error: ${result.error}")
    Result.Loading -> println("Loading...")
}  // Exhaustive - compiler checks all cases!
```

**Benefits of combination:**
- Type safety at compile time
- Exhaustive when expressions
- Clean, maintainable code
- Perfect for state management

## Ответ (RU)

Data классы в Kotlin предназначены для хранения данных и автоматически генерируют методы equals(), hashCode(), toString(), а также copy()...

---

## Follow-ups
- Can sealed class be a data class?
- What are sealed interfaces?
- How to handle nested sealed hierarchies?

## References
- [[c-kotlin-data-classes]]
- [[c-kotlin-sealed-classes]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-sealed-classes-purpose--programming-languages--medium]]
- [[q-data-class-component-functions--programming-languages--easy]]

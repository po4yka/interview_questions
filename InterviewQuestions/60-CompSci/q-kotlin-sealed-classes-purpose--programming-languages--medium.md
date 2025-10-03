---
id: 20251003141005
title: Sealed classes purpose / Назначение sealed классов
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, oop, sealed-classes]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/438
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-sealed-classes
  - c-kotlin-when-expressions

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, sealed-classes, type-hierarchy, when-expressions, oop, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What are sealed classes and why are they needed

# Вопрос (RU)
> Что такое sealed классы и зачем они нужны

---

## Answer (EN)

Sealed classes in Kotlin allow **restricting the set of subclasses** that can be created for a class, providing a strict, closed hierarchy.

**Why they're needed:**

1. **Finite set of states**: Perfect for data that can have a limited number of states
```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}
```

2. **Exhaustive when expressions**: Compiler checks all cases are covered
```kotlin
when (result) {
    is Result.Success -> showData(result.data)
    is Result.Error -> showError(result.message)
    Result.Loading -> showLoading()
    // No 'else' needed - compiler knows all cases!
}
```

3. **Type safety**: All possible types known at compile time

4. **Better than enums**: Can have different properties and methods per subclass

**Benefits:**
- Code is more safe and understandable
- Compiler helps catch missing cases
- Better than using multiple nullable fields
- Perfect for state machines, API responses, navigation

## Ответ (RU)

Sealed классы в Kotlin позволяют ограничить набор подклассов, которые могут быть созданы для этого класса, обеспечивая строгую иерархию...

---

## Follow-ups
- How do sealed classes differ from enums?
- Can sealed classes be abstract?
- What are sealed interfaces (Kotlin 1.5+)?

## References
- [[c-kotlin-sealed-classes]]
- [[c-kotlin-when-expressions]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-sealed-classes-features--programming-languages--medium]]
- [[q-kotlin-data-sealed-classes-combined--programming-languages--medium]]

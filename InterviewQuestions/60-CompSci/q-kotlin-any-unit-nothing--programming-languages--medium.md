---
id: 20251003140902
title: Kotlin special types - Any, Unit, Nothing / Специальные типы в Kotlin
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, type-system]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/30
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-type-system

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, types, any, unit, nothing, type-system, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What do you know about Any, Unit, Nothing types in Kotlin?

# Вопрос (RU)
> Что известно про типы any, unit, nothing в Kotlin ?

---

## Answer (EN)

There are special types in Kotlin with unique purposes:

### Any
- Root type for all non-nullable types in Kotlin (analogous to Object in Java)
- Any object except null inherits from Any
- Used where representation of any possible value except null is required
- Defines basic methods: `equals()`, `hashCode()`, `toString()`

### Unit
- Analogous to `void` in Java, but unlike void, it is a full-fledged object
- Functions that don't return a meaningful result actually return Unit
- Used to indicate that function performs an action but doesn't return a value
- Although Unit return type is usually omitted, it can be specified explicitly

### Nothing
- Type that has no values
- Used to denote "impossibility" - situations when function never completes normally
- Function may loop forever or always throw an exception
- Indicates that this code point is unreachable

**Example:**
```kotlin
fun fail(message: String): Nothing {
    throw IllegalArgumentException(message)
}
```

## Ответ (RU)

Существуют специальные типы Any, Unit и Nothing, которые имеют уникальные цели и применения в языке программирования...

---

## Follow-ups
- How does Any differ from Any?
- When should you explicitly use Unit?
- What are practical use cases for Nothing?

## References
- [[c-kotlin-type-system]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-nothing-purpose--programming-languages--medium]]
- [[q-kotlin-null-safety--programming-languages--medium]]

---
id: 20251003140903
title: Nothing type purpose / Назначение типа Nothing
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, type-system]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/33
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
tags: [kotlin, nothing, type-system, static-analysis, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> Why is the Nothing class needed

# Вопрос (RU)
> Зачем нужен класс nothing

---

## Answer (EN)

The Nothing class has a unique and very specific purpose. It represents a type that has no values and is used to denote operations that never complete normally.

**Key reasons why this type is useful:**

1. **Denoting unreachable code**: When a function never returns control (always throws exception or executes infinite loop), Nothing return type clearly demonstrates this intentional behavior

2. **Helping static code analysis**: Compiler and static analysis tools can use information that certain code has Nothing type to infer that subsequent code is unreachable. This helps in code optimization and error prevention

3. **Improving code readability**: Using it indicates that function doesn't return and shouldn't complete, making code more understandable for developers

**Example:**
```kotlin
fun throwError(message: String): Nothing {
    throw IllegalArgumentException(message)
}

// Compiler knows this code is unreachable
val result = throwError("Error!")
println("This line is unreachable")
```

Nothing is a type without values used to denote operations that don't have normal completion.

## Ответ (RU)

Класс Nothing имеет уникальное и очень специфическое назначение...

---

## Follow-ups
- How does Nothing relate to null?
- What is Nothing? (nullable Nothing)?
- When does compiler infer Nothing type?

## References
- [[c-kotlin-type-system]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-any-unit-nothing--programming-languages--medium]]

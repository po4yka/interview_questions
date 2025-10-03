---
id: 20251003140906
title: Kotlin constants / Константы в Kotlin
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, fundamentals]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/134
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-fundamentals

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, constants, val, const, immutability, difficulty/easy, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What are constants and can they be changed

# Вопрос (RU)
> Что такое константы и можно ли их изменять

---

## Answer (EN)

Constants are fixed values that cannot be changed after their definition. They are used to define values that remain unchanged throughout program execution.

**In Kotlin:**

- **`val`**: Immutable variable (read-only), value assigned once at runtime
```kotlin
val name = "John" // Cannot reassign
```

- **`const val`**: Compile-time constant (must be top-level or in object, primitive or String)
```kotlin
const val MAX_SIZE = 100 // Known at compile time
```

**Key differences:**
- `val` can be initialized at runtime
- `const val` must be known at compile time
- `const val` can only be used with primitive types and String

Constants are **immutable** - their value cannot be changed after definition.

## Ответ (RU)

Константы — это фиксированные значения, которые не могут быть изменены после их определения...

---

## Follow-ups
- What's the difference between val and const val?
- When should you use const vs val?
- Can objects referenced by val be mutated?

## References
- [[c-kotlin-fundamentals]]
- [[moc-kotlin]]

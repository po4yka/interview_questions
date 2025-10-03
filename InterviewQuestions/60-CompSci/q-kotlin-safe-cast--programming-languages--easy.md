---
id: 20251003141003
title: Safe cast operator in Kotlin / Оператор безопасного приведения в Kotlin
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, type-safety]
question_kind: practical
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/357
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-type-safety
  - c-kotlin-null-safety

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, safe-cast, type-conversion, as?, casting, difficulty/easy, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> How to safely cast Any to String in Kotlin to avoid exceptions

# Вопрос (RU)
> Как в Kotlin привести переменную типа Any к типу String безопасно, чтобы избежать исключения

---

## Answer (EN)

Use the **safe cast operator `as?`**, which returns null instead of throwing an exception if the cast is not possible.

**Syntax:**
```kotlin
val stringValue = anyVariable as? String
```

**Comparison:**

| Operator | Success | Failure |
|----------|---------|---------|
| `as` | Returns casted value | Throws `ClassCastException` |
| `as?` | Returns casted value | Returns `null` |

**Examples:**
```kotlin
val any: Any = "Hello"
val str1 = any as? String      // "Hello" (success)
val str2 = any as String        // "Hello" (success)

val number: Any = 42
val str3 = number as? String    // null (safe)
val str4 = number as String     // ClassCastException!

// With Elvis operator
val result = any as? String ?: "default"
```

**When to use:**
- When you're not sure if cast will succeed
- When you want to handle failure gracefully
- To avoid try-catch blocks for casting

## Ответ (RU)

Используйте оператор приведения типов `as?`, который возвращает null вместо выброса исключения, если приведение невозможно. Например: val stringValue = anyVariable as? String

---

## Follow-ups
- When should you use `as` vs `as?`?
- How to handle null results from safe casts?
- What is `is` operator for type checking?

## References
- [[c-kotlin-type-safety]]
- [[c-kotlin-null-safety]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-null-safety--programming-languages--medium]]
- [[q-kotlin-nullable-string-declaration--programming-languages--easy]]

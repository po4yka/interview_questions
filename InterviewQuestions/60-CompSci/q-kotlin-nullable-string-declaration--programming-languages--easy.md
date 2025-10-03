---
id: 20251003141001
title: Nullable String declaration in Kotlin / Объявление nullable String в Kotlin
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, null-safety, syntax]
question_kind: practical
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/231
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-null-safety

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, nullable, string, syntax, null-safety, difficulty/easy, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> How to correctly declare a nullable String variable in Kotlin

# Вопрос (RU)
> Как правильно объявить переменную типа nullable String в Kotlin

---

## Answer (EN)

In Kotlin, to declare a nullable String variable, use the **`?` operator** after the data type.

**Syntax:**
```kotlin
var name: String? = null
```

**Key points:**
- `String` - non-nullable type (cannot be null)
- `String?` - nullable type (can be null)
- Without `?`, compiler won't allow assigning null

**Examples:**
```kotlin
// Nullable variables
var nullable: String? = "Hello"
nullable = null  // OK

// Non-nullable variables
var nonNullable: String = "Hello"
nonNullable = null  // Compilation error!
```

## Ответ (RU)

В Kotlin для объявления переменной типа nullable String используется оператор ?. после типа данных. Например: var name: String? = null

---

## Follow-ups
- What operations are safe on nullable types?
- How to convert nullable to non-nullable?
- What is the difference between `!!` and `?` operators?

## References
- [[c-kotlin-null-safety]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-null-safety--programming-languages--medium]]
- [[q-kotlin-safe-cast--programming-languages--easy]]

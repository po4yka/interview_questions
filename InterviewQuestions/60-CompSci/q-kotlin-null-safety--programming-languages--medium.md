---
id: 20251003140904
title: Kotlin null safety / Безопасность от null в Kotlin
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, null-safety]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/58
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
tags: [kotlin, null-safety, nullable, operators, safe-call, elvis, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What is null safety and how is it written

# Вопрос (RU)
> Что такое null safety и как это пишется

---

## Answer (EN)

Null safety is a concept aimed at preventing runtime errors that occur due to unexpected use of null values (like NullPointerException in Java).

**Kotlin null safety features:**

1. **Nullable types**: Variable types by default don't allow null. Use `?` to make type nullable:
```kotlin
var name: String = "John"     // Cannot be null
var nullable: String? = null  // Can be null
```

2. **Safe call operator** `?.`: Access methods/properties safely:
```kotlin
val length = nullable?.length // Returns null if nullable is null
```

3. **Elvis operator** `?:`: Provide default value:
```kotlin
val length = nullable?.length ?: 0 // Returns 0 if null
```

4. **Not-null assertion** `!!`: Force NPE (not recommended):
```kotlin
val length = nullable!!.length // Throws NPE if null
```

5. **Safe casts** `as?`: Cast safely without exception:
```kotlin
val result = value as? String // Returns null if cast fails
```

Kotlin's null safety prevents most null-related crashes at compile time.

## Ответ (RU)

Null safety, или безопасность относительно null, — это концепция направленная на предотвращение ошибок времени выполнения...

---

## Follow-ups
- What is the difference between platform types and nullable types?
- How to work with Java code that doesn't have null annotations?
- What are best practices for null safety?

## References
- [[c-kotlin-null-safety]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-let-function--programming-languages--easy]]

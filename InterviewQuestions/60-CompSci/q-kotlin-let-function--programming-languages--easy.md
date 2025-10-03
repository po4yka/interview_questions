---
id: 20251003140905
title: Kotlin let function / Функция let в Kotlin
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, scope-functions]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/107
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-scope-functions
  - c-kotlin-null-safety

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, scope-functions, let, null-safety, difficulty/easy, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What is let used for

# Вопрос (RU)
> Для чего нужен let

---

## Answer (EN)

`let` is one of several scope functions in Kotlin standard library that provide more convenient value management, especially when working with potentially null values.

**Main purposes:**

1. **Handling nullable values**: Safe work with variables that may be null
```kotlin
nullable?.let {
    // This block executes only if nullable is not null
    println(it.length)
}
```

2. **Reducing scope**: Limiting variable scope to temporary values
```kotlin
val result = computeValue().let { value ->
    // Use value only in this scope
    transformValue(value)
}
```

3. **Call chaining**: Creating method call chains
```kotlin
value
    .let { it.trim() }
    .let { it.uppercase() }
    .let { println(it) }
```

`let` receives the object as `it` parameter and returns the result of lambda.

## Ответ (RU)

let является одной из нескольких функций расширения, которые входят в стандартную библиотеку языка...

---

## Follow-ups
- What are other scope functions (also, apply, run, with)?
- When to use let vs apply vs run?
- How does let help with immutability?

## References
- [[c-kotlin-scope-functions]]
- [[c-kotlin-null-safety]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-null-safety--programming-languages--medium]]

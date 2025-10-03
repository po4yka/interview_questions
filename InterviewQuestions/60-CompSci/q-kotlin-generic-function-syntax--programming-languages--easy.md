---
id: 20251003141002
title: Generic function syntax in Kotlin / Синтаксис обобщённых функций в Kotlin
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, generics]
question_kind: practical
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/252
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-generics

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, generics, functions, syntax, type-parameters, difficulty/easy, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What syntax is used to declare a generic function in Kotlin

# Вопрос (RU)
> Какой синтаксис используется для объявления обобщенной функции в Kotlin

---

## Answer (EN)

To declare a generic function in Kotlin, use angle brackets `<T>` before the function name:

**Syntax:**
```kotlin
fun <T> functionName(parameter: T): T {
    // function body
}
```

**Examples:**
```kotlin
// Simple generic function
fun <T> identity(value: T): T {
    return value
}

// Multiple type parameters
fun <K, V> mapOf(key: K, value: V): Map<K, V> {
    return mapOf(key to value)
}

// With type constraints
fun <T : Comparable<T>> max(a: T, b: T): T {
    return if (a > b) a else b
}

// Usage
val result = identity(42)        // T inferred as Int
val name = identity("Hello")     // T inferred as String
```

**Type parameter placement:**
- Before function name: `fun <T> name()`
- Before extension receiver: `fun <T> T.extension()`

## Ответ (RU)

Для объявления обобщенной функции в Kotlin используется синтаксис: fun <T> functionName() { ... }

---

## Follow-ups
- What are type constraints (upper bounds)?
- How does type inference work with generics?
- What is reified in inline functions?

## References
- [[c-kotlin-generics]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-inline-functions--programming-languages--medium]]

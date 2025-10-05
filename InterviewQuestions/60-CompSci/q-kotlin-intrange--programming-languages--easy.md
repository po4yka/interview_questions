---
id: 20251003141201
title: IntRange in Kotlin / IntRange в Kotlin
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, ranges]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/1165
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-ranges

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, ranges, intrange, iteration, difficulty/easy, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What is IntRange

# Вопрос (RU)
> Что такое IntRange

---

## Answer (EN)

`IntRange` is a **range of integers** defined by start, end, and step values. It's used for iterations and checking if a number is within a range.

### Creating IntRange

**Using `..` operator (inclusive):**
```kotlin
val range = 1..10          // 1, 2, 3, ..., 10
val charRange = 'a'..'z'   // Character range
```

**Using `until` (exclusive end):**
```kotlin
val range = 1 until 10     // 1, 2, 3, ..., 9 (excludes 10)
```

**Using `downTo` (descending):**
```kotlin
val range = 10 downTo 1    // 10, 9, 8, ..., 1
```

**With step:**
```kotlin
val range = 1..10 step 2   // 1, 3, 5, 7, 9
val desc = 10 downTo 1 step 2  // 10, 8, 6, 4, 2
```

### Usage

**In loops:**
```kotlin
for (i in 1..5) {
    println(i)  // Prints: 1 2 3 4 5
}

for (i in 10 downTo 1 step 2) {
    println(i)  // Prints: 10 8 6 4 2
}
```

**Checking membership:**
```kotlin
val range = 1..10
val isInRange = 5 in range     // true
val isNotInRange = 15 !in range // true
```

**Range properties:**
```kotlin
val range = 1..10
println(range.first)  // 1
println(range.last)   // 10
println(range.step)   // 1
```

### Common Operations

```kotlin
val range = 1..10

// Convert to list
val list = range.toList()  // [1, 2, 3, ..., 10]

// Check if empty
val isEmpty = range.isEmpty()  // false

// Filter, map
val evens = range.filter { it % 2 == 0 }  // [2, 4, 6, 8, 10]
```

**IntRange** is part of Kotlin's progression types along with `LongRange`, `CharRange`, etc.

## Ответ (RU)

Это диапазон целых чисел заданный началом концом и шагом Он используется для итераций и проверки вхождения числа в диапазон

---

## Follow-ups
- What other range types exist in Kotlin?
- How to create custom progressions?
- What is the difference between `..` and `until`?

## References
- [[c-kotlin-ranges]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-for-loop--programming-languages--easy]]
- [[q-kotlin-collections-overview--programming-languages--easy]]

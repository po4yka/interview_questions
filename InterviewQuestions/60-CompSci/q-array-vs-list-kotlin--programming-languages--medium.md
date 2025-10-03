---
id: 20251003140901
title: Array vs List in Kotlin / Различия между массивом и списком в Kotlin
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, collections]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/14
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-collections
  - c-data-structures

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, array, list, collections, performance, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What is the difference between array and list

# Вопрос (RU)
> Чем array отличается от list

---

## Answer (EN)

Arrays and lists are data structures for storing sets of elements.

**Main differences:**

1. **Size**: Arrays have fixed size after creation, while lists are dynamic and can automatically change size when adding or removing elements

2. **Typing**: Arrays can be primitive or object types. In Kotlin arrays are always objects but there are special types for primitives (IntArray, etc.). Lists always contain objects and are generic

3. **Functionality**: Arrays have basic operations, while lists provide a rich set of methods for working with elements

4. **Performance**: Arrays are faster for direct index access. Lists may be less efficient due to dynamic resizing but are more convenient for management

5. **Usage**: Arrays for known size and high-performance index access, lists for flexibility in collection management

**Examples:**
```kotlin
// Array - fixed size
val array = arrayOf(1, 2, 3)

// List - dynamic
val list = mutableListOf(1, 2, 3)
list.add(4) // Can grow
```

## Ответ (RU)

Массивы и списки представляют собой структуры данных для хранения наборов элементов. [Full Russian text preserved in source]

---

## Follow-ups
- When should you use Array vs List?
- What are specialized array types (IntArray, etc.)?
- How to convert between arrays and lists?

## References
- [[c-kotlin-collections]]
- [[c-data-structures]]
- [[moc-kotlin]]

## Related Questions
- [[q-linkedlist-arraylist-insert-behavior--programming-languages--medium]]

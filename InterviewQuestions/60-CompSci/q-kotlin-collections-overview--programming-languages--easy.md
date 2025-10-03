---
id: 20251003141006
title: Kotlin collections overview / Обзор коллекций в Kotlin
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, collections]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/443
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-collections

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, collections, list, set, map, mutable, immutable, difficulty/easy, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What collections do you know

# Вопрос (RU)
> Какие коллекции знаешь

---

## Answer (EN)

In Kotlin there are **immutable (read-only)** and **mutable** collections:

### Immutable Collections (Read-only interfaces)
- **List** - ordered collection allowing duplicates
- **Set** - unordered collection of unique elements
- **Map** - key-value pairs with unique keys

### Mutable Collections
- **MutableList** - can add/remove elements
- **MutableSet** - can add/remove unique elements  
- **MutableMap** - can add/remove key-value pairs

### Specialized Implementations
- **ArrayList** - dynamic array implementation of MutableList
- **LinkedList** - doubly-linked list implementation
- **HashSet** - hash table implementation of MutableSet
- **HashMap** - hash table implementation of MutableMap

**Creation examples:**
```kotlin
// Immutable (read-only references)
val list = listOf(1, 2, 3)
val set = setOf("a", "b", "c")
val map = mapOf("key" to "value")

// Mutable
val mutableList = mutableListOf(1, 2, 3)
val mutableSet = mutableSetOf("a", "b")
val mutableMap = mutableMapOf("key" to "value")
```

**Note**: "Immutable" means read-only reference, not necessarily immutable data.

## Ответ (RU)

В Kotlin есть неизменяемые и изменяемые коллекции. Неизменяемые включают List, Set и Map. Изменяемые - MutableList, MutableSet и MutableMap. Также существуют специализированные коллекции: ArrayList, HashSet и HashMap.

---

## Follow-ups
- What's the difference between immutable and read-only?
- When to use ArrayList vs LinkedList?
- How does Set ensure uniqueness?

## References
- [[c-kotlin-collections]]
- [[moc-kotlin]]

## Related Questions
- [[q-list-set-map-differences--programming-languages--easy]]
- [[q-kotlin-immutable-collections--programming-languages--easy]]

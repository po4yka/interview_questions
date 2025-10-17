---
id: "20251015082237085"
title: "Kotlin Collections Overview / Обзор коллекций Kotlin"
topic: programming-languages
difficulty: easy
status: draft
created: 2025-10-13
tags: - collections
  - immutable
  - kotlin
  - list
  - map
  - mutable
  - programming-languages
  - set
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-programming-languages
related_questions: []
---
# Какие коллекции знаешь?

# Question (EN)
> What collections do you know?

# Вопрос (RU)
> Какие коллекции знаешь?

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

---

## Ответ (RU)

В Kotlin есть неизменяемые и изменяемые коллекции. Неизменяемые включают List, Set и Map. Изменяемые - MutableList, MutableSet и MutableMap. Также существуют специализированные коллекции: ArrayList, HashSet и HashMap.


---

## Related Questions

### Android Implementation
- [[q-kak-izmenit-kolichestvo-kolonok-v-recyclerview-v-zavisimosti-ot-orientatsii--programming-languages--easy]] - Data Structures

### Kotlin Language Features
- [[q-kotlin-immutable-collections--programming-languages--easy]] - Data Structures
- [[q-collection-implementations--programming-languages--easy]] - Data Structures
- [[q-list-set-map-differences--programming-languages--easy]] - Data Structures
- [[q-arraylist-linkedlist-vector-difference--programming-languages--medium]] - Data Structures
- [[q-kotlin-collections--kotlin--medium]] - Data Structures
- [[q-kotlin-collections--kotlin--easy]] - Data Structures

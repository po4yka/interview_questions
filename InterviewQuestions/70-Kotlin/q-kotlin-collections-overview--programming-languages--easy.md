---
id: 20251012-12271111114
title: "Kotlin Collections Overview / Обзор коллекций Kotlin"
aliases: []
topic: programming-languages
subtopics: [functions, class-features, java-interop]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-programming-languages
related: [q-supervisor-scope-vs-coroutine-scope--kotlin--medium, q-nothing-instances--programming-languages--easy, q-lambdas-java-kotlin-syntax--programming-languages--medium]
created: 2025-10-13
updated: 2025-10-31
tags:
  - 
  - difficulty/easy
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

В Kotlin есть **неизменяемые (read-only)** и **изменяемые** коллекции:

### Неизменяемые коллекции (Read-only интерфейсы)
- **List** - упорядоченная коллекция, допускающая дубликаты
- **Set** - неупорядоченная коллекция уникальных элементов
- **Map** - пары ключ-значение с уникальными ключами

### Изменяемые коллекции
- **MutableList** - можно добавлять/удалять элементы
- **MutableSet** - можно добавлять/удалять уникальные элементы
- **MutableMap** - можно добавлять/удалять пары ключ-значение

### Специализированные реализации
- **ArrayList** - реализация MutableList на основе динамического массива
- **LinkedList** - реализация на основе двусвязного списка
- **HashSet** - реализация MutableSet на основе хеш-таблицы
- **HashMap** - реализация MutableMap на основе хеш-таблицы

**Примеры создания:**
```kotlin
// Неизменяемые (read-only ссылки)
val list = listOf(1, 2, 3)
val set = setOf("a", "b", "c")
val map = mapOf("key" to "value")

// Изменяемые
val mutableList = mutableListOf(1, 2, 3)
val mutableSet = mutableSetOf("a", "b")
val mutableMap = mutableMapOf("key" to "value")
```

**Примечание**: "Неизменяемая" означает read-only ссылку, а не обязательно неизменяемые данные.


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

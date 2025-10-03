---
id: 20251003140102
title: What mechanism allows creating immutable collections in Kotlin / Какой механизм позволяет создавать иммутабельные коллекции в Kotlin
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, collections]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/124
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-collections
  - c-collections

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, collections, collections,immutability, difficulty/easy, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What mechanism allows creating immutable collections in Kotlin

# Вопрос (RU)
> Какой механизм позволяет создавать иммутабельные коллекции в Kotlin

---

## Answer (EN)

In Kotlin, immutable collections are created using a mechanism based on interfaces from the kotlin.collections package. Specifically, factory functions such as listOf(), setOf(), and mapOf() are used to create immutable collections. These functions return collections implementing the List, Set, and Map interfaces respectively. Collections created with these functions are immutable, meaning that after creation, elements cannot be added or removed. For example, using listOf() creates an immutable list.

## Ответ (RU)

В Kotlin для создания иммутабельных коллекций используется механизм, основанный на использовании интерфейсов из пакета kotlin.collections. В частности, для создания неизменяемых коллекций применяются функции-фабрики, такие как listOf(), setOf() и mapOf(). Эти функции возвращают коллекции, реализующие интерфейсы List, Set и Map соответственно. При этом, коллекции, созданные с помощью этих функций, являются неизменяемыми (иммутабельными), то есть после их создания нельзя добавить или удалить элементы. Например, при использовании listOf() создается неизменяемый список.

---

## Follow-ups
- How does this compare to other collection types?
- What are the performance implications?
- When should you use this approach?

## References
- [[c-kotlin-collections]]
- [[c-collections]]
- [[moc-kotlin]]

## Related Questions
- [[q-list-set-map-differences--programming-languages--easy]]

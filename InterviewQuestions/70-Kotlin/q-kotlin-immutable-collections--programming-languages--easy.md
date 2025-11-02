---
id: lang-096
title: "Kotlin Immutable Collections / Неизменяемые коллекции Kotlin"
aliases: [Kotlin Immutable Collections, Неизменяемые коллекции Kotlin]
topic: programming-languages
subtopics: [collections, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-kotlin-val-vs-var--kotlin--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [collections, difficulty/easy, immutability, programming-languages]
date created: Friday, October 31st 2025, 6:29:34 pm
date modified: Saturday, November 1st 2025, 5:43:25 pm
---

# Какой Механизм Позволяет Создавать Иммутабельные Коллекции В Kotlin?

**English**: What mechanism allows creating immutable collections in Kotlin?

## Answer (EN)
In Kotlin, immutable collections are created using a mechanism based on interfaces from the kotlin.collections package. Specifically, factory functions such as listOf(), setOf(), and mapOf() are used to create immutable collections. These functions return collections implementing the List, Set, and Map interfaces respectively. Collections created with these functions are immutable, meaning that after creation, elements cannot be added or removed. For example, using listOf() creates an immutable list.

## Ответ (RU)
В Kotlin для создания иммутабельных коллекций используется механизм, основанный на использовании интерфейсов из пакета kotlin.collections. В частности, для создания неизменяемых коллекций применяются функции-фабрики, такие как listOf(), setOf() и mapOf(). Эти функции возвращают коллекции, реализующие интерфейсы List, Set и Map соответственно. При этом, коллекции, созданные с помощью этих функций, являются неизменяемыми (иммутабельными), то есть после их создания нельзя добавить или удалить элементы. Например, при использовании listOf() создается неизменяемый список.

## Related Questions

- [[q-kotlin-val-vs-var--kotlin--easy]]
-
-

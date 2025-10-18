---
id: 20251012-154373
title: "Kotlin Immutable Collections / Неизменяемые коллекции Kotlin"
topic: kotlin
difficulty: easy
status: draft
moc: moc-kotlin
related: [q-kotlin-val-vs-var--kotlin--easy, q-kotlin-coroutines-overview--programming-languages--medium, q-serialization-basics--programming-languages--medium]
created: 2025-10-15
tags:
  - collections
  - immutability
  - kotlin
  - programming-languages
---
# Какой механизм позволяет создавать иммутабельные коллекции в Kotlin?

**English**: What mechanism allows creating immutable collections in Kotlin?

## Answer (EN)
In Kotlin, immutable collections are created using a mechanism based on interfaces from the kotlin.collections package. Specifically, factory functions such as listOf(), setOf(), and mapOf() are used to create immutable collections. These functions return collections implementing the List, Set, and Map interfaces respectively. Collections created with these functions are immutable, meaning that after creation, elements cannot be added or removed. For example, using listOf() creates an immutable list.

## Ответ (RU)
В Kotlin для создания иммутабельных коллекций используется механизм, основанный на использовании интерфейсов из пакета kotlin.collections. В частности, для создания неизменяемых коллекций применяются функции-фабрики, такие как listOf(), setOf() и mapOf(). Эти функции возвращают коллекции, реализующие интерфейсы List, Set и Map соответственно. При этом, коллекции, созданные с помощью этих функций, являются неизменяемыми (иммутабельными), то есть после их создания нельзя добавить или удалить элементы. Например, при использовании listOf() создается неизменяемый список.

## Related Questions

- [[q-kotlin-val-vs-var--kotlin--easy]]
- [[q-kotlin-coroutines-overview--programming-languages--medium]]
- [[q-serialization-basics--programming-languages--medium]]

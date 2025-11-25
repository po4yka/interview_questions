---
id: lang-096
title: "Kotlin Immutable Collections / Неизменяемые коллекции Kotlin"
aliases: [Kotlin Immutable Collections, Неизменяемые коллекции Kotlin]
topic: kotlin
subtopics: [collections, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-kotlin-val-vs-var--kotlin--easy]
created: 2025-10-15
updated: 2025-11-10
tags: [collections, difficulty/easy, immutability, kotlin]
date created: Friday, October 31st 2025, 6:29:34 pm
date modified: Tuesday, November 25th 2025, 8:53:50 pm
---

# Вопрос (RU)
> Какой механизм позволяет создавать неизменяемые (только для чтения) коллекции в Kotlin?

# Question (EN)
> What mechanism allows creating immutable (read-only) collections in Kotlin?

## Ответ (RU)
В Kotlin так называемые иммутабельные (только для чтения) коллекции создаются за счёт:

- разделения интерфейсов коллекций только для чтения (`List`, `Set`, `Map`) и их изменяемых вариантов (`MutableList`, `MutableSet`, `MutableMap`) в пакете `kotlin.collections`;
- функций-фабрик `listOf()`, `setOf()` и `mapOf()`, которые возвращают представления только для чтения с типами `List`, `Set` и `Map`.

Коллекции, возвращаемые `listOf()`, `setOf()` и `mapOf()`, нельзя изменять через интерфейсы только для чтения: они не предоставляют операции `add`/`remove`/`put`. Однако это не строгая гарантия глубокой иммутабельности: если реализация основана на изменяемой коллекции, на которую есть другие ссылки, её содержимое может изменяться через эти изменяемые ссылки.

Ключевой практический механизм — разделение на уровне типов: используйте `List`/`Set`/`Map`, когда потребителям нужна коллекция только для чтения, и `MutableList`/`MutableSet`/`MutableMap`, когда требуется возможность изменения.

См. также: [[c-kotlin]], [[c-collections]].

## Answer (EN)
In Kotlin, so-called immutable (read-only) collections are created using:

- the separation between read-only collection interfaces (`List`, `Set`, `Map`) and their mutable counterparts (`MutableList`, `MutableSet`, `MutableMap`) in the `kotlin.collections` package;
- factory functions such as `listOf()`, `setOf()`, and `mapOf()`, which return read-only views typed as `List`, `Set`, and `Map`.

Collections returned by `listOf()`, `setOf()`, and `mapOf()` cannot be modified through the read-only interfaces: they do not expose `add`/`remove`/`put` operations. However, this is not a strict deep immutability guarantee: if the underlying implementation is backed by a mutable collection that is referenced elsewhere, its contents may still change via that mutable reference.

The key practical mechanism is the type-level separation: use `List`/`Set`/`Map` when you want a read-only view for consumers, and use `MutableList`/`MutableSet`/`MutableMap` when mutation is required.

## Дополнительные Вопросы (RU)

- В чём ключевые отличия этого подхода от Java?
- Когда вы бы использовали этот механизм на практике?
- Какие распространённые подводные камни стоит учитывать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- Документация Kotlin: https://kotlinlang.org/docs/home.html

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-kotlin-val-vs-var--kotlin--easy]]

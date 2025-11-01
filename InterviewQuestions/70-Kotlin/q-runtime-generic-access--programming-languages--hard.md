---
id: 20251012-1227111175
title: "Runtime Generic Access / Доступ к дженерикам во время выполнения"
aliases: [Runtime Generic Access, Доступ к дженерикам во время выполнения]
topic: programming-languages
subtopics: [generics, type-system, reification]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-programming-languages
related: [q-coroutine-dispatchers--programming-languages--medium, q-os-fundamentals-concepts--computer-science--hard, q-what-is-garbage-in-gc--programming-languages--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [generics, kotlin, programming-languages, reified, type-erasure, difficulty/hard]
date created: Friday, October 3rd 2025, 4:39:28 pm
date modified: Sunday, October 26th 2025, 1:37:22 pm
---

# Можно Ли Получить В Runtime Доступ К Типу Дженерика?

# Question (EN)
> Can you access generic type at runtime?

# Вопрос (RU)
> Можно ли получить в runtime доступ к типу дженерика?

---

## Answer (EN)

By default, no, because generics are erased (Type Erasure) during compilation. If using inline fun, you can make the generic 'real' (reified). Also, to get type in a class, you can use KClass<T>, and for complex generics (List<T>, Map<K, V>) use typeOf<T>() only with reified.

---

## Ответ (RU)

По умолчанию нельзя, потому что дженерики стираются (Type Erasure) во время компиляции. Если используем inline fun, можно сделать дженерик "реальным" (reified). Также для получения типа в классе можно использовать KClass<T>, а для сложных дженериков (List<T>, Map<K, V>) использовать typeOf<T>() только с reified

## Related Questions

- [[q-what-is-garbage-in-gc--programming-languages--easy]]
- [[q-os-fundamentals-concepts--computer-science--hard]]
- [[q-coroutine-dispatchers--programming-languages--medium]]

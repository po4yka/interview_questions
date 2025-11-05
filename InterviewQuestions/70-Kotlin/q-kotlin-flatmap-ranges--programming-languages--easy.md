---
id: lang-038
title: "Kotlin Flatmap Ranges / flatMap и диапазоны в Kotlin"
aliases: [flatMap и диапазоны в Kotlin, Kotlin Flatmap Ranges]
topic: programming-languages
subtopics: [collections, functional-programming]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-inline-function-limitations--kotlin--medium, q-retry-exponential-backoff-flow--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [collections, difficulty/easy, flatMap, programming-languages, ranges]
date created: Friday, October 31st 2025, 6:29:33 pm
date modified: Saturday, November 1st 2025, 5:43:25 pm
---

# Какой Результат Выполнения Выражения Val Result = (1..3).flatMap { listOf(it, it * 2) }?

# Question (EN)
> What is the result of executing val result = (1..3).flatMap { listOf(it, it * 2) }?

# Вопрос (RU)
> Какой результат выполнения выражения val result = (1..3).flatMap { listOf(it, it * 2) }?

---

## Answer (EN)

The result of executing the expression will be the list [1, 2, 2, 4, 3, 6].

---

## Ответ (RU)

Результат выполнения выражения будет список [1, 2, 2, 4, 3, 6].

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-inline-function-limitations--kotlin--medium]]
-
- [[q-retry-exponential-backoff-flow--kotlin--medium]]

---
id: lang-038
title: Kotlin Flatmap Ranges / flatMap и диапазоны в Kotlin
aliases:
- flatMap и диапазоны в Kotlin
- Kotlin Flatmap Ranges
topic: kotlin
subtopics:
- collections
- functional-programming
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- q-inline-function-limitations--kotlin--medium
- q-retry-exponential-backoff-flow--kotlin--medium
created: 2025-10-15
updated: 2025-11-09
tags:
- collections
- difficulty/easy
- flatMap
- kotlin
- ranges
anki_cards:
- slug: lang-038-0-en
  language: en
  anki_id: 1768326287506
  synced_at: '2026-01-23T17:03:51.194275'
- slug: lang-038-0-ru
  language: ru
  anki_id: 1768326287531
  synced_at: '2026-01-23T17:03:51.195833'
---
# Вопрос (RU)
> Какой результат выполнения выражения `val result = (1..3).flatMap { listOf(it, it * 2) }`?

# Question (EN)
> What is the result of executing `val result = (1..3).flatMap { listOf(it, it * 2) }`?

## Ответ (RU)

Результат выполнения выражения будет список `[1, 2, 2, 4, 3, 6]`.

## Answer (EN)

The result of executing the expression will be the list `[1, 2, 2, 4, 3, 6]`.

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Related Questions

- [[q-inline-function-limitations--kotlin--medium]]
- [[q-retry-exponential-backoff-flow--kotlin--medium]]

## Дополнительные Вопросы (RU)
- В чем ключевые отличия этого подхода от Java?
- Когда бы вы использовали этот прием на практике?
- Каковы распространенные ошибки, которых следует избегать?
## Ссылки (RU)
- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
## Связанные Вопросы (RU)
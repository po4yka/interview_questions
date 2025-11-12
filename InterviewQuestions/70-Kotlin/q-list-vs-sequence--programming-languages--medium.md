---
id: lang-001
title: "List Vs Sequence / List против Sequence"
aliases: [List Vs Sequence, List против Sequence]
topic: kotlin
subtopics: [collections, performance, lazy-evaluation]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-collections, q-list-vs-sequence--kotlin--medium]
created: 2024-10-13
updated: 2025-11-11
tags: [collections, difficulty/medium, kotlin, list, programming-languages, sequence]
---
# Вопрос (RU)
> В чем разница между работой с `List` и работой с `Sequence`?

# Question (EN)
> What is the difference between working with `List` and working with `Sequence`?

---

## Ответ (RU)

- `List` в Kotlin — это материализованная коллекция в памяти. Операции (`map`, `filter` и т.п.), как правило, выполняются немедленно и возвращают новые коллекции, создавая промежуточные списки на каждом шаге цепочки.
- `Sequence` — это ленивое представление последовательности элементов (не коллекция). Промежуточные операции не создают новых коллекций; элементы обрабатываются по одному при выполнении терминальной операции (например, `toList()`, `first()`, `count()`).
- Работа с `List` обычно эффективнее для небольших коллекций и коротких цепочек операций из-за меньших накладных расходов.
- `Sequence` полезен для:
  - больших коллекций или потенциально бесконечных источников;
  - длинных цепочек преобразований, где важно избежать создания множества промежуточных коллекций;
  - случаев, когда можно остановить обработку раньше при выполнении условия (short-circuiting).
- Важно: `Sequence` обычно однопроходный, и повторный обход требует повторного создания `Sequence` или явной материализации (например, `toList()`), в отличие от уже материализованного `List`.

---

## Answer (EN)

- In Kotlin, a `List` is a materialized collection in memory. Operations like `map`, `filter`, etc. are generally eager: they run immediately and return new collections, creating intermediate lists at each step of a chain.
- A `Sequence` is a lazy view of elements (not a collection). Intermediate operations do not create new collections; elements are processed one by one when a terminal operation is invoked (e.g., `toList()`, `first()`, `count()`).
- Working with a `List` is often more efficient for small collections and short pipelines because it has lower per-element overhead.
- `Sequence`s are useful for:
  - large collections or potentially infinite sources;
  - long transformation chains where avoiding multiple intermediate collections matters;
  - cases where you can stop early once a condition is met (short-circuiting).
- Note: A `Sequence` is typically single-pass; to traverse again you usually recreate the sequence or materialize it (e.g., `toList()`), whereas a `List` is already materialized and can be iterated multiple times cheaply.

---

## Дополнительные вопросы (RU)

- В чем ключевые отличия этого подхода от Java?
- Когда вы бы использовали это на практике?
- Какие распространенные подводные камни следует учитывать?

## Follow-ups (EN)

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [[c-collections]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## References (EN)

- [[c-kotlin]]
- [[c-collections]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные вопросы (RU)

### Реализация в Android
- [[q-what-problems-can-there-be-with-list-items--android--easy]] — Структуры данных

### Особенности языка Kotlin
- [[q-list-vs-sequence--kotlin--medium]] — Структуры данных
- [[q-kotlin-immutable-collections--programming-languages--easy]] — Структуры данных

## Related Questions (EN)

### Android Implementation
- [[q-what-problems-can-there-be-with-list-items--android--easy]] - Data Structures

### Kotlin Language Features
- [[q-list-vs-sequence--kotlin--medium]] - Data Structures
- [[q-kotlin-immutable-collections--programming-languages--easy]] - Data Structures

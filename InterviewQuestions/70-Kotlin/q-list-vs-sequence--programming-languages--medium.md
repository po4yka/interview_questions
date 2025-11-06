---
id: lang-001
title: "List Vs Sequence / List против Sequence"
aliases: [List Vs Sequence, List против Sequence]
topic: programming-languages
subtopics: [collections, lazy-evaluation, performance]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-data-class-component-functions--programming-languages--easy, q-iterator-order-guarantee--programming-languages--medium, q-iterator-pattern--design-patterns--medium]
created: 2025-10-13
updated: 2025-10-31
tags: [collections, difficulty/medium, kotlin, list, programming-languages, sequence]
---
# В Чем Разница Между Работой С List И Работой С Sequence

# Вопрос (RU)
> В чем разница между работой с list и работой с sequence

---

# Question (EN)
> What is the difference between working with list and sequence?

## Ответ (RU)

List является жадной коллекцией, где все операции выполняются немедленно и целиком над всеми элементами сразу. Sequence является ленивой коллекцией, где операции обрабатывают элементы по мере необходимости через цепочку. List подходит для небольших коллекций и может использовать больше памяти из-за промежуточных коллекций. Sequence эффективен для больших коллекций и уменьшает использование памяти.


---

## Answer (EN)

List is an eager collection where all operations are executed immediately and entirely on all elements at once. Sequence is a lazy collection where operations process elements as needed through a chain. List is suitable for small collections and may use more memory due to intermediate collections. Sequence is efficient for large collections and reduces memory usage.

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

### Android Implementation
- [[q-what-problems-can-there-be-with-list-items--android--easy]] - Data Structures

### Kotlin Language Features
-  - Data Structures
-  - Data Structures
-  - Data Structures
-  - Data Structures
- [[q-list-vs-sequence--kotlin--medium]] - Data Structures
- [[q-kotlin-immutable-collections--programming-languages--easy]] - Data Structures

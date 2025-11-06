---
id: lang-067
title: "Iterator Order Guarantee / Гарантия порядка Iterator"
aliases: [Iterator Order Guarantee, Гарантия порядка Iterator]
topic: programming-languages
subtopics: [collections, iterators, ordering]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-collections, c-iterators, q-iterator-concept--programming-languages--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [collections, difficulty/medium, iterators, kotlin, programming-languages]
---
# После Перебирания Данных Итератором, Гарантируется Ли Очередность Получения Этих Данных?

# Вопрос (RU)
> После перебирания данных итератором, гарантируется ли очередность получения этих данных?

---

# Question (EN)
> After iterating data with an iterator, is the order of obtaining this data guaranteed?

## Ответ (RU)

Гарантируется только в том случае, если структура данных поддерживает порядок (например, List, LinkedList). Если коллекция неупорядоченная (например, HashSet, HashMap.keySet()), порядок может быть произвольным и не повторяться.

## Answer (EN)

It is guaranteed only if the data structure supports order (e.g., List, LinkedList). If the collection is unordered (e.g., HashSet, HashMap.keySet()), the order may be arbitrary and not repeatable.

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-java-object-comparison--programming-languages--easy]]
- [[q-inheritance-composition-aggregation--oop--medium]]
-

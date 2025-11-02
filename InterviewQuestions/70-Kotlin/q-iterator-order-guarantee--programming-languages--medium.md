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
moc: moc-programming-languages
related: [c-collections, c-iterators, q-iterator-concept--programming-languages--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [collections, difficulty/medium, iterators, kotlin, programming-languages]
date created: Friday, October 31st 2025, 6:32:07 pm
date modified: Saturday, November 1st 2025, 5:43:25 pm
---

# После Перебирания Данных Итератором, Гарантируется Ли Очередность Получения Этих Данных?

# Question (EN)
> After iterating data with an iterator, is the order of obtaining this data guaranteed?

# Вопрос (RU)
> После перебирания данных итератором, гарантируется ли очередность получения этих данных?

---

## Answer (EN)

It is guaranteed only if the data structure supports order (e.g., List, LinkedList). If the collection is unordered (e.g., HashSet, HashMap.keySet()), the order may be arbitrary and not repeatable.

---

## Ответ (RU)

Гарантируется только в том случае, если структура данных поддерживает порядок (например, List, LinkedList). Если коллекция неупорядоченная (например, HashSet, HashMap.keySet()), порядок может быть произвольным и не повторяться.

## Related Questions

- [[q-java-object-comparison--programming-languages--easy]]
- [[q-inheritance-composition-aggregation--oop--medium]]
-

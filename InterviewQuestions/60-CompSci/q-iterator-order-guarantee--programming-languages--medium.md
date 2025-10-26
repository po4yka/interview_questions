---
id: 20251012-1227111152
title: "Iterator Order Guarantee / Гарантия порядка Iterator"
topic: computer-science
difficulty: medium
status: draft
moc: moc-cs
related: [q-abstract-factory-pattern--design-patterns--medium, q-inheritance-composition-aggregation--oop--medium, q-java-object-comparison--programming-languages--easy]
created: 2025-10-15
tags: [collections, iterators, kotlin, programming-languages]
date created: Friday, October 3rd 2025, 4:14:02 pm
date modified: Sunday, October 26th 2025, 12:05:23 pm
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
- [[q-abstract-factory-pattern--design-patterns--medium]]

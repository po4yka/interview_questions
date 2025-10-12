---
tags:
  - collections
  - iterators
  - kotlin
  - programming-languages
difficulty: medium
status: draft
---

# После перебирания данных итератором, гарантируется ли очередность получения этих данных?

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


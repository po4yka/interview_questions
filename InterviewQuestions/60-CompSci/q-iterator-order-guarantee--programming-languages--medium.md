---
tags:
  - collections
  - iterators
  - kotlin
  - programming-languages
difficulty: medium
status: reviewed
---

# После перебирания данных итератором, гарантируется ли очередность получения этих данных?

**English**: After iterating data with an iterator, is the order of obtaining this data guaranteed?

## Answer

It is guaranteed only if the data structure supports order (e.g., List, LinkedList). If the collection is unordered (e.g., HashSet, HashMap.keySet()), the order may be arbitrary and not repeatable.

## Ответ

Гарантируется только в том случае, если структура данных поддерживает порядок (например, List, LinkedList). Если коллекция неупорядоченная (например, HashSet, HashMap.keySet()), порядок может быть произвольным и не повторяться.


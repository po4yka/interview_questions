---
tags:
  - collections
  - data structures
  - kotlin
  - programming-languages
difficulty: medium
status: draft
---

# В чем разница ArrayList, LinkedList, Vector

**English**: What is the difference between ArrayList, LinkedList, Vector?

## Answer

ArrayList implements a mutable array with fast random access but slow insertions/deletions. LinkedList implements a doubly-linked list with fast insertions/deletions but slow random access. Vector is similar to ArrayList but synchronized for thread safety and slower due to synchronization.

## Ответ

ArrayList реализует изменяемый массив с быстрым произвольным доступом, но медленными вставками/удалениями. LinkedList реализует двунаправленный список с быстрыми вставками/удалениями, но медленным произвольным доступом. Vector похож на ArrayList, но синхронизирован для потокобезопасности и медленнее из-за синхронизации.


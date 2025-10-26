---
id: 20251012-1227111162
title: "List Vs Sequence / List против Sequence"
topic: programming-languages
difficulty: medium
status: draft
created: 2025-10-13
tags: [collections, kotlin, list, programming-languages, sequence]
moc: moc-programming-languages
related: [q-data-class-component-functions--programming-languages--easy, q-iterator-order-guarantee--programming-languages--medium, q-iterator-pattern--design-patterns--medium]
date created: Friday, October 3rd 2025, 4:14:02 pm
date modified: Sunday, October 26th 2025, 12:08:07 pm
---

# В Чем Разница Между Работой С List И Работой С Sequence

# Question (EN)
> What is the difference between working with list and sequence?

# Вопрос (RU)
> В чем разница между работой с list и работой с sequence

---

## Answer (EN)

List is an eager collection where all operations are executed immediately and entirely on all elements at once. Sequence is a lazy collection where operations process elements as needed through a chain. List is suitable for small collections and may use more memory due to intermediate collections. Sequence is efficient for large collections and reduces memory usage.

---

## Ответ (RU)

List является жадной коллекцией, где все операции выполняются немедленно и целиком над всеми элементами сразу. Sequence является ленивой коллекцией, где операции обрабатывают элементы по мере необходимости через цепочку. List подходит для небольших коллекций и может использовать больше памяти из-за промежуточных коллекций. Sequence эффективен для больших коллекций и уменьшает использование памяти.


---

## Related Questions

### Android Implementation
- [[q-what-problems-can-there-be-with-list-items--android--easy]] - Data Structures

### Kotlin Language Features
- [[q-list-set-map-differences--programming-languages--easy]] - Data Structures
- [[q-collection-implementations--programming-languages--easy]] - Data Structures
- [[q-arraylist-linkedlist-vector-difference--programming-languages--medium]] - Data Structures
- [[q-equals-hashcode-contracts--programming-languages--hard]] - Data Structures
- [[q-list-vs-sequence--kotlin--medium]] - Data Structures
- [[q-kotlin-immutable-collections--programming-languages--easy]] - Data Structures

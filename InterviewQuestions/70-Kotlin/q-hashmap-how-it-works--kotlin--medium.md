---
id: lang-044
title: "Hashmap How It Works / Как работает HashMap"
aliases: [Hashmap How It Works, Как работает HashMap]
topic: kotlin
subtopics: [collections, data-structures, hash-tables]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-collections, c-hash-map]
created: 2025-10-15
updated: 2025-11-09
tags: [collections, data-structures, difficulty/medium, hash-tables, hashmap, kotlin]
date created: Friday, October 31st 2025, 6:31:04 pm
date modified: Tuesday, November 25th 2025, 8:53:51 pm
---
# Вопрос (RU)
> Как работает `HashMap`?

---

# Question (EN)
> How does `HashMap` work?

## Ответ (RU)

`HashMap` (и стандартная реализация `HashMap`/`MutableMap` в Kotlin/JVM) хранит пары ключ-значение и использует хеш-таблицу для быстрого поиска, вставки и удаления.

Ключевые моменты:

- Для каждого ключа вычисляется `hashCode()`. На основе хеша и размера внутреннего массива выбирается индекс корзины (bucket).
- В каждой корзине может храниться несколько записей: при коллизиях (разные ключи с одинаковым индексом) элементы хранятся в связанной структуре (цепочка/список; на JVM это делается аналогично Java `HashMap`).
- При поиске по ключу сначала выбирается корзина по хешу, затем внутри неё элементы сравниваются через `equals()` до нахождения нужного ключа.
- При росте количества элементов и превышении порога загрузки (load factor) внутренний массив расширяется (resize/rehash), элементы перераспределяются по новым корзинам.
- Амортизированное время операций `get`/`put`/`remove` в среднем O(1); в худшем случае при большом числе коллизий — O(n).
- Корректная работа требует согласованной реализации `equals()` и `hashCode()` у ключей; изменение полей ключа, влияющих на хеш и равенство, после вставки в карту может привести к тому, что элемент станет «ненаходимым».
- Обычный `HashMap` не гарантирует порядок обхода элементов (для упорядоченного обхода используется, например, `LinkedHashMap`).

Также см. [[c-hash-map]] и [[c-collections]].

## Answer (EN)

`HashMap` (and the standard `HashMap`/`MutableMap` implementation in Kotlin/JVM) stores key-value pairs and uses a hash table to provide fast lookup, insertion, and removal.

Key points:

- For each key, `hashCode()` is computed. Based on the hash and the internal array size, an index of a bucket is chosen.
- Each bucket can hold multiple entries: on collisions (different keys mapping to the same index), entries are stored in a linked structure (chain/list; on the JVM this is implemented similarly to Java's `HashMap`).
- For `get`, the map picks the bucket by hash, then scans entries in that bucket comparing keys via `equals()` until it finds the target key.
- When the number of entries grows beyond a load factor threshold, the internal array is resized (rehash), and entries are redistributed across new buckets.
- The amortized time complexity of `get`/`put`/`remove` is O(1) on average; in the worst case with many collisions it can degrade to O(n).
- Correct behavior relies on keys having consistent `equals()` and `hashCode()` implementations; mutating key fields that affect hash/equality after insertion can make entries unreachable.
- A regular `HashMap` does not guarantee iteration order (for a predictable iteration order you would use e.g. `LinkedHashMap`).

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия реализации от Java `HashMap`?
- Когда на практике стоит использовать `HashMap`?
- Каковы распространенные ошибки и подводные камни при использовании `HashMap`?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-how-suspend-function-detects-suspension--kotlin--hard]]

## Related Questions

- [[q-how-suspend-function-detects-suspension--kotlin--hard]]

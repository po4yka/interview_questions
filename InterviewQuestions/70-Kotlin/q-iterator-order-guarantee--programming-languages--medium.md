---
id: lang-067
title: "Iterator Order Guarantee / Гарантия порядка Iterator"
aliases: [Iterator Order Guarantee, Гарантия порядка Iterator]
topic: kotlin
subtopics: [collections, iterators, ordering]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-collections, q-iterator-concept--programming-languages--easy]
created: 2025-10-15
updated: 2025-11-09
tags: [collections, difficulty/medium, iterators, kotlin]
---
# Вопрос (RU)
> После перебирания данных итератором, гарантируется ли очередность получения этих данных?

---

# Question (EN)
> After iterating data with an iterator, is the order of obtaining this data guaranteed?

## Ответ (RU)

Порядок перебора элементов итератором зависит от контракта конкретной коллекции/структуры данных, а не от самого механизма `Iterator`. См. также [[c-collections]].

- Для упорядоченных коллекций (например, `List`, `ArrayList`, `LinkedList`, а также коллекций с контрактом сохранения порядка вставки, таких как `LinkedHashSet`, `LinkedHashMap`) итератор гарантированно обходит элементы в определённом порядке (например, в порядке индексов или вставки), при условии что коллекция не была структурно изменена некорректным образом во время обхода.
- Для неупорядоченных коллекций (например, `HashSet`, `HashMap.keySet()` и другие хеш-коллекции без определённого контракта порядка) порядок обхода официально не определён и не должен использоваться в логике программы, даже если на конкретной JVM/платформе он кажется стабильным.
- В Kotlin (особенно на JVM) фактический порядок итерации для стандартных коллекций обычно наследует контракт соответствующей реализации платформы (например, Java-коллекций), но это не меняет общего правила: полагаться можно только на явно задокументированный контракт коллекции.

## Answer (EN)

The iteration order is determined by the contract of the specific collection/data structure, not by the `Iterator` mechanism itself.

- For ordered collections (e.g., `List`, `ArrayList`, `LinkedList`, and collections whose contract specifies insertion-order traversal such as `LinkedHashSet`, `LinkedHashMap`), the iterator is guaranteed to traverse elements in that defined order (e.g., index order or insertion order), provided the collection is not structurally modified in an unsupported way during iteration.
- For unordered collections (e.g., `HashSet`, `HashMap.keySet()` and other hash-based collections without a specified order contract), the traversal order is unspecified and must not be relied upon in program logic, even if it appears stable on a particular JVM/platform.
- In Kotlin (especially on the JVM), the actual iteration order of standard collections typically follows the contract of the underlying platform implementations (e.g., Java collections), but the general rule remains: you may only rely on order when it is explicitly documented as part of the collection's contract.

---

## Дополнительные вопросы (RU)

- В чем ключевые отличия этого поведения от Java?
- Когда бы вы использовали это на практике?
- Каких распространенных ошибок следует избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные вопросы (RU)

- [[q-java-object-comparison--programming-languages--easy]]
- [[q-inheritance-composition-aggregation--oop--medium]]

## Related Questions

- [[q-java-object-comparison--programming-languages--easy]]
- [[q-inheritance-composition-aggregation--oop--medium]]

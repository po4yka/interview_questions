---
id: 20251005-222646
title: "Kotlin Collections / Коллекции в Kotlin"
aliases: []

# Classification
topic: kotlin
subtopics: [collections, list, set, map, data-structures]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-kotlin-generic-function-syntax--programming-languages--easy, q-coroutine-profiling--kotlin--hard, q-suspend-functions-basics--kotlin--easy]

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [kotlin, collections, list, set, map, data-structures, difficulty/easy]
---
# Question (EN)
> What do you know about Collections in Kotlin?
# Вопрос (RU)
> Что вы знаете о коллекциях в Kotlin?

---

## Answer (EN)

`Collection` usually contains a number of objects of the same type. Objects in a collection are called `elements` or `items`. For example, all the students in a department form a collection that can be used to calculate their average age. The following collection types are relevant for Kotlin:

- **List** is an ordered collection with access to elements by indices – integer numbers that reflect their position. Elements can occur more than once in a list.

- **Set** is a collection of unique elements. It reflects the mathematical abstraction of set: a group of objects without repetitions.

- **Map (or dictionary)** is a set of key-value pairs. Keys are unique, and each of them maps to exactly one value. The values can be duplicates. Maps are useful for storing logical connections between objects.

### Collection Types

The Kotlin Standard Library provides implementations for basic collection types: sets, lists, and maps. A pair of interfaces represent each collection type:

- A **read-only** interface that provides operations for accessing collection elements. The read-only collection types are `covariant` (collection types have the same subtyping relationship as the element types. If a `Rectangle` class inherits from `Shape`, you can use a `List<Rectangle>` anywhere the `List<Shape>` is required.)

- A **mutable** interface that extends the corresponding read-only interface with write operations: adding, removing, and updating its elements.

The mutable collections aren't covariant; otherwise, this would lead to runtime failures. If `MutableList<Rectangle>` was a subtype of `MutableList<Shape>`, you could insert other `Shape` inheritors (for example, `Circle`) into it, thus violating its `Rectangle` type argument.

Below is a diagram of the Kotlin collection interfaces:

![Kotlin Collections Diagram](https://raw.githubusercontent.com/swayangjit/Android-Interview-Questions/master/Kotlin/res/collections-diagram.png)

## Ответ (RU)

`Collection` обычно содержит несколько объектов одного типа. Объекты в коллекции называются `элементами` или `items`. Например, все студенты на факультете образуют коллекцию, которую можно использовать для вычисления их среднего возраста. Для Kotlin актуальны следующие типы коллекций:

- **List** — это упорядоченная коллекция с доступом к элементам по индексам – целым числам, которые отражают их позицию. Элементы могут встречаться в списке более одного раза.

- **Set** — это коллекция уникальных элементов. Она отражает математическую абстракцию множества: группу объектов без повторений.

- **Map (или словарь)** — это набор пар ключ-значение. Ключи уникальны, и каждый из них соответствует ровно одному значению. Значения могут дублироваться. Maps полезны для хранения логических связей между объектами.

### Типы коллекций

Стандартная библиотека Kotlin предоставляет реализации для базовых типов коллекций: множеств, списков и карт (map). Пара интерфейсов представляет каждый тип коллекции:

- **Интерфейс только для чтения**, который предоставляет операции для доступа к элементам коллекции. Типы коллекций только для чтения являются `ковариантными` (типы коллекций имеют такое же отношение подтипов, как и типы элементов. Если класс `Rectangle` наследуется от `Shape`, вы можете использовать `List<Rectangle>` везде, где требуется `List<Shape>`.)

- **Изменяемый интерфейс**, который расширяет соответствующий интерфейс только для чтения операциями записи: добавлением, удалением и обновлением элементов.

Изменяемые коллекции не являются ковариантными; в противном случае это привело бы к ошибкам во время выполнения. Если бы `MutableList<Rectangle>` был подтипом `MutableList<Shape>`, вы могли бы вставить в него другие наследники `Shape` (например, `Circle`), тем самым нарушив его аргумент типа `Rectangle`.

Ниже представлена диаграмма интерфейсов коллекций Kotlin:

![Диаграмма коллекций Kotlin](https://raw.githubusercontent.com/swayangjit/Android-Interview-Questions/master/Kotlin/res/collections-diagram.png)

---

## References
- [Kotlin Collections Overview](https://kotlinlang.org/docs/reference/collections-overview.html)

## Related Questions

### Related (Easy)
- [[q-data-structures-overview--algorithms--easy]] - Data Structures

### Advanced (Harder)
- [[q-kotlin-collections--kotlin--medium]] - Collections
- [[q-kotlin-map-flatmap--kotlin--medium]] - Collections
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines

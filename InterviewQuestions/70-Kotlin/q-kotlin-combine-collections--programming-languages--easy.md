---
id: lang-007
title: "Kotlin Combine Collections / Объединение коллекций Kotlin"
aliases: ["Kotlin Combine Collections", "Объединение коллекций Kotlin"]
topic: kotlin
subtopics: [collections]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-collections, c-kotlin, q-channels-vs-flow--kotlin--medium]
created: 2025-10-13
updated: 2025-11-09
tags: [difficulty/easy]
date created: Thursday, October 16th 2025, 4:16:12 pm
date modified: Tuesday, November 25th 2025, 8:53:51 pm
---

# Вопрос (RU)
> Какая функция Kotlin используется для объединения двух коллекций?

---

# Question (EN)
> What Kotlin function is used to combine two collections?

## Ответ (RU)

Оператор `+` (функция `plus`) используется для объединения двух коллекций в Kotlin.

**Принцип работы:**

Оператор `+` создает новую коллекцию, содержащую элементы из обеих исходных коллекций. Исходные коллекции не изменяются, даже если они изменяемые (mutable).

**Примеры использования:**

```kotlin
// Объединение списков
val list1 = listOf(1, 2, 3)
val list2 = listOf(4, 5, 6)
val combined = list1 + list2  // [1, 2, 3, 4, 5, 6]

// Объединение множеств (результат - Set)
val set1 = setOf("a", "b", "c")
val set2 = setOf("c", "d", "e")
val combinedSet = set1 + set2  // [a, b, c, d, e] - дубликаты удаляются, возвращается Set

// Добавление одного элемента
val list = listOf(1, 2, 3)
val newList = list + 4  // [1, 2, 3, 4]

// Объединение Map (результат - новый Map)
val map1 = mapOf("a" to 1, "b" to 2)
val map2 = mapOf("b" to 20, "c" to 3)
val combinedMap = map1 + map2  // {a=1, b=20, c=3} - значения из второй карты перекрывают первую по одинаковым ключам
```

**Альтернативные методы:**

```kotlin
// plus() - явный вызов функции
val result1 = list1.plus(list2)

// union() - для множеств (возвращает Set)
val unionSet = set1.union(set2)

// addAll() - для изменяемых коллекций (изменяет коллекцию на месте)
val mutableList = mutableListOf(1, 2, 3)
mutableList.addAll(listOf(4, 5, 6))
```

**Важные особенности:**

- Оператор `+` доступен для разных типов коллекций и всегда возвращает новую коллекцию.
- Исходные коллекции не изменяются при использовании `+`/`plus`, даже если они mutable.
- Для `Set` дубликаты автоматически удаляются, результат соответствует семантике множества.
- Для `Map` при совпадении ключей значение из второй коллекции перезаписывает значение из первой в результирующей карте.

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого подхода от Java?
- Когда вы бы использовали это на практике?
- Какие распространенные ошибки стоит избегать?

## Ссылки (RU)

- [[c-kotlin]]
- [[c-collections]]
- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

### Реализация В Android
- [[q-kotlin-collections--kotlin--medium]] - Структуры данных

### Особенности Языка Kotlin
- [[q-kotlin-collections--kotlin--easy]] - Структуры данных

---

## Answer (EN)

The `+` operator (the `plus` function) is used to combine two collections in Kotlin.

Key points:

- `+` creates a new collection containing elements from both operands; the original collections are not modified (even if they are mutable).
- It is available for lists, sets, maps, and works with single elements as well.

Examples:

```kotlin
// Combine lists
val list1 = listOf(1, 2, 3)
val list2 = listOf(4, 5, 6)
val combined = list1 + list2  // [1, 2, 3, 4, 5, 6]

// Combine sets (result is a Set)
val set1 = setOf("a", "b", "c")
val set2 = setOf("c", "d", "e")
val combinedSet = set1 + set2  // [a, b, c, d, e] - duplicates removed, returns a Set

// Add single element
val list = listOf(1, 2, 3)
val newList = list + 4  // [1, 2, 3, 4]

// Combine maps (result is a new Map)
val map1 = mapOf("a" to 1, "b" to 2)
val map2 = mapOf("b" to 20, "c" to 3)
val combinedMap = map1 + map2  // {a=1, b=20, c=3} - entries from the second map override on key collisions
```

Alternative methods:

- `plus()` explicit call: `val result = list1.plus(list2)`
- `union()` for sets (returns a `Set`): `val unionSet = set1.union(set2)`
- `addAll()` for mutable collections (modifies in place):
  - `mutableList.addAll(listOf(4, 5, 6))`

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [[c-kotlin]]
- [[c-collections]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

### Android Implementation
- [[q-kotlin-collections--kotlin--medium]] - Data Structures

### Kotlin Language Features
- [[q-kotlin-collections--kotlin--easy]] - Data Structures

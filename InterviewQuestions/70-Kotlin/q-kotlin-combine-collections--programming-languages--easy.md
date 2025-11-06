---
id: lang-007
title: "Kotlin Combine Collections / Объединение коллекций Kotlin"
aliases: ["Kotlin Combine Collections, Объединение коллекций Kotlin"]
topic: programming-languages
subtopics: [class-features, java-interop, operators]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-channels-vs-flow--kotlin--medium, q-custom-dispatchers-limited-parallelism--kotlin--hard, q-kotlin-vs-java-class-creation--programming-languages--medium]
created: 2025-10-13
updated: 2025-10-31
tags: [difficulty/easy]
---
# Какая Функция Kotlin Используется Для Объединения Двух Коллекций?

# Вопрос (RU)
> Какая функция Kotlin используется для объединения двух коллекций?

---

# Question (EN)
> What Kotlin function is used to combine two collections?

## Ответ (RU)

Оператор + (функция plus) используется для объединения двух коллекций в Kotlin.

**Принцип работы:**

Оператор `+` создает новую коллекцию, содержащую элементы из обеих исходных коллекций. Исходные коллекции остаются неизменными.

**Примеры использования:**

```kotlin
// Объединение списков
val list1 = listOf(1, 2, 3)
val list2 = listOf(4, 5, 6)
val combined = list1 + list2  // [1, 2, 3, 4, 5, 6]

// Объединение множеств
val set1 = setOf("a", "b", "c")
val set2 = setOf("c", "d", "e")
val combinedSet = set1 + set2  // [a, b, c, d, e] - дубликаты удаляются

// Добавление одного элемента
val list = listOf(1, 2, 3)
val newList = list + 4  // [1, 2, 3, 4]

// Объединение Map
val map1 = mapOf("a" to 1, "b" to 2)
val map2 = mapOf("c" to 3, "d" to 4)
val combinedMap = map1 + map2  // {a=1, b=2, c=3, d=4}
```

**Альтернативные методы:**

```kotlin
// plus() - явный вызов функции
val result1 = list1.plus(list2)

// union() - для множеств (возвращает Set)
val unionSet = set1.union(set2)

// addAll() - для изменяемых коллекций
val mutableList = mutableListOf(1, 2, 3)
mutableList.addAll(listOf(4, 5, 6))
```

**Важные особенности:**

- Оператор `+` работает с неизменяемыми коллекциями
- Всегда создается новая коллекция
- Исходные коллекции не изменяются
- Для Set дубликаты автоматически удаляются
- Для Map при совпадении ключей значение из второй коллекции перезаписывает значение из первой


---

## Answer (EN)

The + operator (plus function)

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

### Android Implementation
-  - Data Structures

### Kotlin Language Features
- [[q-kotlin-immutable-collections--programming-languages--easy]] - Data Structures
-  - Data Structures
-  - Data Structures
-  - Data Structures
- [[q-kotlin-collections--kotlin--medium]] - Data Structures
- [[q-kotlin-collections--kotlin--easy]] - Data Structures

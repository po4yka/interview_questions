---
id: "20251015082237109"
title: "Kotlin Combine Collections / Объединение коллекций Kotlin"
topic: programming-languages
difficulty: easy
status: draft
created: 2025-10-13
tags: - collections
  - kotlin
  - programming-languages
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-programming-languages
related_questions: []
---
# Какая функция Kotlin используется для объединения двух коллекций?

# Question (EN)
> What Kotlin function is used to combine two collections?

# Вопрос (RU)
> Какая функция Kotlin используется для объединения двух коллекций?

---

## Answer (EN)

The + operator (plus function)

---

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

## Related Questions

### Android Implementation
- [[q-kak-izmenit-kolichestvo-kolonok-v-recyclerview-v-zavisimosti-ot-orientatsii--programming-languages--easy]] - Data Structures

### Kotlin Language Features
- [[q-kotlin-immutable-collections--programming-languages--easy]] - Data Structures
- [[q-collection-implementations--programming-languages--easy]] - Data Structures
- [[q-list-set-map-differences--programming-languages--easy]] - Data Structures
- [[q-arraylist-linkedlist-vector-difference--programming-languages--medium]] - Data Structures
- [[q-kotlin-collections--kotlin--medium]] - Data Structures
- [[q-kotlin-collections--kotlin--easy]] - Data Structures

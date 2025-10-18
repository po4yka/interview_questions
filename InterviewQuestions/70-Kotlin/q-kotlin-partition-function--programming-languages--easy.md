---
id: 20251012-12271111146
title: "Kotlin Partition Function / Функция partition в Kotlin"
topic: computer-science
difficulty: easy
status: draft
moc: moc-kotlin
related: [q-kotlin-any-inheritance--programming-languages--easy, q-fan-in-fan-out-channels--kotlin--hard, q-continuation-cps-internals--kotlin--hard]
created: 2025-10-15
tags:
  - collections
  - functions
  - kotlin
  - programming-languages
---
# Что делает функция коллекций partition()?

# Question (EN)
> What does the collection function partition() do?

# Вопрос (RU)
> Что делает функция коллекций partition()?

---

## Answer (EN)


The `partition` function splits a collection into two lists based on a predicate: one for elements matching the predicate, one for those that don't.

### Syntax
```kotlin
val (matching, notMatching) = collection.partition { predicate }
```

### Examples

**1. Split Numbers**
```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6)
val (even, odd) = numbers.partition { it % 2 == 0 }

println(even)  // [2, 4, 6]
println(odd)   // [1, 3, 5]
```

**2. Filter Users**
```kotlin
data class User(val name: String, val age: Int)

val users = listOf(
    User("Alice", 17),
    User("Bob", 25),
    User("Charlie", 16)
)

val (adults, minors) = users.partition { it.age >= 18 }
// adults: [User("Bob", 25)]
// minors: [User("Alice", 17), User("Charlie", 16)]
```

**3. Validate Input**
```kotlin
val inputs = listOf("abc", "123", "def", "456")
val (letters, numbers) = inputs.partition {
    it.all { char -> char.isLetter() }
}
```

### Return Type
```kotlin
fun <T> Iterable<T>.partition(
    predicate: (T) -> Boolean
): Pair<List<T>, List<T>>
```

### Performance
- O(n) time complexity
- Creates two new lists
- Evaluates predicate once per element

---
---

## Ответ (RU)


Функция `partition` разделяет коллекцию на два списка на основе предиката: один для элементов соответствующих предикату, один для несоответствующих.

### Синтаксис
```kotlin
val (matching, notMatching) = collection.partition { predicate }
```

### Примеры

**1. Разделить числа**
```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6)
val (even, odd) = numbers.partition { it % 2 == 0 }

println(even)  // [2, 4, 6]
println(odd)   // [1, 3, 5]
```

**2. Фильтровать пользователей**
```kotlin
data class User(val name: String, val age: Int)

val users = listOf(
    User("Alice", 17),
    User("Bob", 25),
    User("Charlie", 16)
)

val (adults, minors) = users.partition { it.age >= 18 }
// adults: [User("Bob", 25)]
// minors: [User("Alice", 17), User("Charlie", 16)]
```

**3. Валидация ввода**
```kotlin
val inputs = listOf("abc", "123", "def", "456")
val (letters, numbers) = inputs.partition {
    it.all { char -> char.isLetter() }
}
```

### Тип возврата
```kotlin
fun <T> Iterable<T>.partition(
    predicate: (T) -> Boolean
): Pair<List<T>, List<T>>
```

### Производительность
- O(n) временная сложность
- Создает два новых списка
- Вычисляет предикат один раз на элемент

---

## Related Questions

- [[q-kotlin-any-inheritance--programming-languages--easy]]
- [[q-fan-in-fan-out-channels--kotlin--hard]]
- [[q-continuation-cps-internals--kotlin--hard]]


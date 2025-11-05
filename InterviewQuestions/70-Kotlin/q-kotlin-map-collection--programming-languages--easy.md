---
id: lang-008
title: "Kotlin Map Collection / Map коллекция в Kotlin"
aliases: [Kotlin Map Collection, Map коллекция в Kotlin]
topic: programming-languages
subtopics: [collections, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-13
updated: 2025-10-31
tags: [collections, difficulty/easy, map, programming-languages]
moc: moc-kotlin
related: [q-kotlin-property-delegates--programming-languages--medium, q-visibility-modifiers-kotlin--kotlin--medium]
date created: Friday, October 31st 2025, 6:30:31 pm
date modified: Saturday, November 1st 2025, 5:43:25 pm
---
# Расскажи Про Коллекцию Map

# Вопрос (RU)
> Расскажи про коллекцию Map

---

# Question (EN)
> Tell me about the Map collection

## Ответ (RU)


Функция `map` трансформирует каждый элемент коллекции используя заданную функцию трансформации.

### Базовое Использование
```kotlin
val numbers = listOf(1, 2, 3, 4, 5)
val doubled = numbers.map { it * 2 }
// Результат: [2, 4, 6, 8, 10]
```

### Распространенные Паттерны

**1. Трансформация объектов**
```kotlin
data class User(val name: String, val age: Int)
data class UserDto(val name: String)

val users = listOf(User("Alice", 25), User("Bob", 30))
val dtos = users.map { UserDto(it.name) }
```

**2. Строковые операции**
```kotlin
val names = listOf("alice", "bob", "charlie")
val uppercase = names.map { it.uppercase() }
// ["ALICE", "BOB", "CHARLIE"]
```

**3. Вложенные коллекции**
```kotlin
val matrix = listOf(
    listOf(1, 2, 3),
    listOf(4, 5, 6)
)
val flattened = matrix.map { row ->
    row.map { it * 2 }
}
// [[2, 4, 6], [8, 10, 12]]
```

### Варианты

**mapNotNull** - Трансформация и фильтрация null:
```kotlin
val strings = listOf("1", "2", "abc", "3")
val numbers = strings.mapNotNull { it.toIntOrNull() }
// [1, 2, 3]
```

**mapIndexed** - Доступ к индексу:
```kotlin
val indexed = listOf("a", "b", "c").mapIndexed { index, value ->
    "$index: $value"
}
// ["0: a", "1: b", "2: c"]
```

**flatMap** - Map и flatten:
```kotlin
val nested = listOf(1, 2, 3).flatMap { listOf(it, it * 2) }
// [1, 2, 2, 4, 3, 6]
```

---
---

## Answer (EN)


The `map` function transforms each element of a collection using a given transformation function.

### Basic Usage
```kotlin
val numbers = listOf(1, 2, 3, 4, 5)
val doubled = numbers.map { it * 2 }
// Result: [2, 4, 6, 8, 10]
```

### Common Patterns

**1. Object Transformation**
```kotlin
data class User(val name: String, val age: Int)
data class UserDto(val name: String)

val users = listOf(User("Alice", 25), User("Bob", 30))
val dtos = users.map { UserDto(it.name) }
```

**2. String Operations**
```kotlin
val names = listOf("alice", "bob", "charlie")
val uppercase = names.map { it.uppercase() }
// ["ALICE", "BOB", "CHARLIE"]
```

**3. Nested Collections**
```kotlin
val matrix = listOf(
    listOf(1, 2, 3),
    listOf(4, 5, 6)
)
val flattened = matrix.map { row ->
    row.map { it * 2 }
}
// [[2, 4, 6], [8, 10, 12]]
```

### Variants

**mapNotNull** - Transform and filter nulls:
```kotlin
val strings = listOf("1", "2", "abc", "3")
val numbers = strings.mapNotNull { it.toIntOrNull() }
// [1, 2, 3]
```

**mapIndexed** - Access index:
```kotlin
val indexed = listOf("a", "b", "c").mapIndexed { index, value ->
    "$index: $value"
}
// ["0: a", "1: b", "2: c"]
```

**flatMap** - Map and flatten:
```kotlin
val nested = listOf(1, 2, 3).flatMap { listOf(it, it * 2) }
// [1, 2, 2, 4, 3, 6]
```

---
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
-  - Data Structures
-  - Data Structures
-  - Data Structures
- [[q-kotlin-immutable-collections--programming-languages--easy]] - Data Structures
- [[q-kotlin-collections--kotlin--medium]] - Data Structures
- [[q-kotlin-map-flatmap--kotlin--medium]] - Data Structures

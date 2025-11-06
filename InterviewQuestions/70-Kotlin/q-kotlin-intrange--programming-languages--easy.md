---
id: lang-060
title: "Kotlin Intrange / IntRange в Kotlin"
aliases: [IntRange в Kotlin, Kotlin Intrange]
topic: programming-languages
subtopics: [collections, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-coroutine-context-elements--kotlin--hard, q-kotlin-constructors--kotlin--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/easy, intrange, iteration, programming-languages, ranges]
---
# Что Такое IntRange?

# Вопрос (RU)
> Что такое IntRange?

---

# Question (EN)
> What is IntRange?

## Ответ (RU)

`IntRange` — это **диапазон целых чисел**, определённый начальным, конечным значением и шагом. Используется для итераций и проверки вхождения числа в диапазон.

### Создание IntRange

**Используя оператор `..` (включительно):**
```kotlin
val range = 1..10          // 1, 2, 3, ..., 10
val charRange = 'a'..'z'   // Диапазон символов
```

**Используя `until` (конец не включается):**
```kotlin
val range = 1 until 10     // 1, 2, 3, ..., 9 (не включает 10)
```

**Используя `downTo` (по убыванию):**
```kotlin
val range = 10 downTo 1    // 10, 9, 8, ..., 1
```

**С шагом:**
```kotlin
val range = 1..10 step 2   // 1, 3, 5, 7, 9
val desc = 10 downTo 1 step 2  // 10, 8, 6, 4, 2
```

### Использование

**В циклах:**
```kotlin
for (i in 1..5) {
    println(i)  // Выводит: 1 2 3 4 5
}

for (i in 10 downTo 1 step 2) {
    println(i)  // Выводит: 10 8 6 4 2
}
```

**Проверка вхождения:**
```kotlin
val range = 1..10
val isInRange = 5 in range     // true
val isNotInRange = 15 !in range // true
```

**Свойства диапазона:**
```kotlin
val range = 1..10
println(range.first)  // 1
println(range.last)   // 10
println(range.step)   // 1
```

### Распространённые Операции

```kotlin
val range = 1..10

// Преобразование в список
val list = range.toList()  // [1, 2, 3, ..., 10]

// Проверка на пустоту
val isEmpty = range.isEmpty()  // false

// Filter, map
val evens = range.filter { it % 2 == 0 }  // [2, 4, 6, 8, 10]
```

**IntRange** является частью типов прогрессий Kotlin вместе с `LongRange`, `CharRange` и т.д.

## Answer (EN)

`IntRange` is a **range of integers** defined by start, end, and step values. It's used for iterations and checking if a number is within a range.

### Creating IntRange

**Using `..` operator (inclusive):**
```kotlin
val range = 1..10          // 1, 2, 3, ..., 10
val charRange = 'a'..'z'   // Character range
```

**Using `until` (exclusive end):**
```kotlin
val range = 1 until 10     // 1, 2, 3, ..., 9 (excludes 10)
```

**Using `downTo` (descending):**
```kotlin
val range = 10 downTo 1    // 10, 9, 8, ..., 1
```

**With step:**
```kotlin
val range = 1..10 step 2   // 1, 3, 5, 7, 9
val desc = 10 downTo 1 step 2  // 10, 8, 6, 4, 2
```

### Usage

**In loops:**
```kotlin
for (i in 1..5) {
    println(i)  // Prints: 1 2 3 4 5
}

for (i in 10 downTo 1 step 2) {
    println(i)  // Prints: 10 8 6 4 2
}
```

**Checking membership:**
```kotlin
val range = 1..10
val isInRange = 5 in range     // true
val isNotInRange = 15 !in range // true
```

**Range properties:**
```kotlin
val range = 1..10
println(range.first)  // 1
println(range.last)   // 10
println(range.step)   // 1
```

### Common Operations

```kotlin
val range = 1..10

// Convert to list
val list = range.toList()  // [1, 2, 3, ..., 10]

// Check if empty
val isEmpty = range.isEmpty()  // false

// Filter, map
val evens = range.filter { it % 2 == 0 }  // [2, 4, 6, 8, 10]
```

**IntRange** is part of Kotlin's progression types along with `LongRange`, `CharRange`, etc.

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-kotlin-constructors--kotlin--easy]]
- [[q-coroutine-context-elements--kotlin--hard]]
-

---
id: kotlin-002
title: Equality Operators == vs === / Операторы равенства == vs ===
aliases:
- Equality Operators == vs ===
- Операторы равенства == vs ===
topic: kotlin
subtopics:
- equality
- operators
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository - Kotlin Batch 2
status: draft
moc: moc-kotlin
related:
- c-equality
- c-kotlin
created: 2025-10-05
updated: 2025-11-09
tags:
- comparison
- difficulty/easy
- equality
- kotlin
- operators
anki_cards:
- slug: kotlin-002-0-en
  language: en
  difficulty: 0.3
  tags:
  - Kotlin
  - difficulty::easy
  - equality
  - operators
- slug: kotlin-002-0-ru
  language: ru
  difficulty: 0.3
  tags:
  - Kotlin
  - difficulty::easy
  - equality
  - operators
---
# Вопрос (RU)
> В чем разница между == и === в Kotlin?

---

# Question (EN)
> What is the difference between == and === in Kotlin?

---

## Ответ (RU)

В Kotlin есть два типа равенства: **структурное** и **ссылочное**.

### == (Структурное равенство)

Проверяет, равны ли **значения** объектов. Для ссылочных типов при ненулевом левом операнде ведет себя как вызов `equals()` с проверкой на null: `a?.equals(b) ?: (b === null)`.

```kotlin
val a = "hello"
val b = "hello"
println(a == b)  // true - одинаковое содержимое

val list1 = listOf(1, 2, 3)
val list2 = listOf(1, 2, 3)
println(list1 == list2)  // true - одинаковое содержимое
```

Для примитивных типов (например, `Int`) `==` сравнивает значения, как ожидается.

### === (Ссылочное равенство)

Проверяет, указывают ли две ссылки на **один и тот же объект**. Эквивалентно оператору `==` в Java для ссылочных типов.

```kotlin
val list1 = mutableListOf(1, 2, 3)
val list2 = mutableListOf(1, 2, 3)
println(list1 === list2)  // false - разные объекты
println(list1 === list1)  // true - тот же объект
```

Важно: не полагайтесь на `===` для строк или чисел как на способ проверки "одинакового значения" — он проверяет именно идентичность объекта/ссылки, а не содержимое.

### Итоговая Таблица

| Оператор | Назначение | Эквивалент в Java | Null-safe |
|----------|------------|-------------------|-----------|
| `==` | Структурное равенство (содержимое) | `equals()` с null-safe семантикой | Да (`a?.equals(b) ?: (b === null)`) |
| `===` | Ссылочное равенство (ссылка) | `==` (для ссылок) | Нет |

### Примеры

```kotlin
data class Person(val name: String, val age: Int)

val person1 = Person("Alice", 25)
val person2 = Person("Alice", 25)
val person3 = person1

// Структурное равенство
println(person1 == person2)  // true - одинаковые данные
println(person1 == person3)  // true - одинаковые данные

// Ссылочное равенство
println(person1 === person2)  // false - разные объекты
println(person1 === person3)  // true - та же ссылка
```

**Итог (RU)**: `==` проверяет структурное равенство (равные значения/содержимое) с null-safe семантикой, фактически вызывая `equals()`. `===` проверяет ссылочное равенство (та же ссылка/объект). Используйте `==` для сравнения значений, `===` — для проверки, что две переменные указывают на один и тот же объект.

---

## Answer (EN)

Kotlin has two types of equality: **structural** and **referential**.

### == (Structural Equality)

Checks if objects have **equal values**. For reference types with a non-null left operand it behaves like calling `equals()` with a null-safe check: `a?.equals(b) ?: (b === null)`.

```kotlin
val a = "hello"
val b = "hello"
println(a == b)  // true - same content

val list1 = listOf(1, 2, 3)
val list2 = listOf(1, 2, 3)
println(list1 == list2)  // true - same content
```

For primitive types (e.g., `Int`), `==` compares values as expected.

### === (Referential Equality)

Checks if two references point to the **same object**. Equivalent to the `==` operator in Java for reference types.

```kotlin
val list1 = mutableListOf(1, 2, 3)
val list2 = mutableListOf(1, 2, 3)
println(list1 === list2)  // false - different objects
println(list1 === list1)  // true - same object
```

Note: do not rely on `===` for strings or numbers as a way to check "same value" — it only checks object/reference identity, not content.

### Summary Table

| Operator | Purpose | Java Equivalent | Null Safe |
|----------|---------|-----------------|-----------|
| `==` | Structural equality (content) | `equals()` with null-safe semantics | Yes (`a?.equals(b) ?: (b === null)`) |
| `===` | Referential equality (reference) | `==` (for references) | No |

### Examples

```kotlin
data class Person(val name: String, val age: Int)

val person1 = Person("Alice", 25)
val person2 = Person("Alice", 25)
val person3 = person1

// Structural equality
println(person1 == person2)  // true - same data
println(person1 == person3)  // true - same data

// Referential equality
println(person1 === person2)  // false - different objects
println(person1 === person3)  // true - same reference
```

**English Summary**: `==` checks structural equality (equal values/content) with null-safe semantics, effectively calling `equals()`. `===` checks referential equality (same object reference). Use `==` for comparing values, `===` for checking if two variables point to the same object.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Equality - Kotlin Documentation](https://kotlinlang.org/docs/reference/equality.html)
- [[c-kotlin]]
- [[c-equality]]

## Related Questions

### Advanced (Harder)
- [[q-instant-search-flow-operators--kotlin--medium]] - `Flow`
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-flow-operators--kotlin--medium]] - `Flow`

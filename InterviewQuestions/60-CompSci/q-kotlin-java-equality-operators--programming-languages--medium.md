---
id: 20251003141004
title: Equality operators in Java vs Kotlin / Операторы равенства в Java и Kotlin
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, java, operators]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/421
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-operators
  - c-java-kotlin-differences

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, java, operators, equality, comparison, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What is the difference between double equals in Java and Kotlin?

# Вопрос (RU)
> Чем отличаются двойное равно в Java и Kotlin?

---

## Answer (EN)

In Java and Kotlin, `==` has different semantics:

### Java

- `==` checks **reference equality** (same object in memory)
- `.equals()` checks **structural equality** (same values)

```java
String a = new String("hello");
String b = new String("hello");

a == b           // false (different references)
a.equals(b)      // true (same values)
```

### Kotlin

- `==` checks **structural equality** (calls `.equals()` under the hood)
- `===` checks **reference equality** (same object in memory)

```kotlin
val a = "hello"
val b = "hello"

a == b           // true (structural equality)
a === b          // true (string interning)

val c = StringBuilder("hello").toString()
a == c           // true (same values)
a === c          // false (different objects)
```

**Comparison table:**

| Purpose | Java | Kotlin |
|---------|------|--------|
| Reference equality | `==` | `===` |
| Structural equality | `.equals()` | `==` |
| Null-safe comparison | Manual null checks | Built-in (`==` handles null) |

**Key difference**: Kotlin's `==` is null-safe - `null == null` is true!

## Ответ (RU)

В Java оператор == проверяет, указывают ли две переменные на один и тот же объект в памяти. Для сравнения значений строк используется метод equals(). В Kotlin оператор == сравнивает значения объектов аналогично методу equals() в Java, а для сравнения ссылок используется оператор ===.

---

## Follow-ups
- How does `==` handle null values in Kotlin?
- What is string interning?
- When should you use `===` instead of `==`?

## References
- [[c-kotlin-operators]]
- [[c-java-kotlin-differences]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-null-safety--programming-languages--medium]]
- [[q-equals-hashcode-rules--programming-languages--medium]]

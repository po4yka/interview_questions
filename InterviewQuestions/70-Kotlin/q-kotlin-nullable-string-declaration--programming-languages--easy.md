---
id: lang-026
title: "Kotlin Nullable String Declaration / Объявление nullable String в Kotlin"
aliases: [Kotlin Nullable String Declaration, Объявление nullable String в Kotlin]
topic: programming-languages
subtopics: [null-safety, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-coroutine-job-lifecycle--kotlin--medium, q-kotlin-operator-overloading--kotlin--medium, q-launch-vs-async--kotlin--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/easy, null-safety, nullable, programming-languages, string, syntax]
date created: Friday, October 31st 2025, 6:30:57 pm
date modified: Saturday, November 1st 2025, 5:43:25 pm
---

# Как Правильно Объявить Переменную Типа Nullable String В Kotlin?

# Question (EN)
> How to correctly declare a nullable String variable in Kotlin?

# Вопрос (RU)
> Как правильно объявить переменную типа nullable String в Kotlin?

---

## Answer (EN)

In Kotlin, to declare a nullable String variable, use the **`?` operator** after the data type.

**Syntax:**
```kotlin
var name: String? = null
```

**Key points:**
- `String` - non-nullable type (cannot be null)
- `String?` - nullable type (can be null)
- Without `?`, compiler won't allow assigning null

**Examples:**
```kotlin
// Nullable variables
var nullable: String? = "Hello"
nullable = null  // OK

// Non-nullable variables
var nonNullable: String = "Hello"
nonNullable = null  // Compilation error!
```

---

## Ответ (RU)

В Kotlin для объявления переменной типа nullable String используется **оператор `?`** после типа данных.

**Синтаксис:**
```kotlin
var name: String? = null
```

**Ключевые моменты:**
- `String` - ненулевой тип (не может быть null)
- `String?` - nullable тип (может быть null)
- Без `?` компилятор не позволит присвоить null

**Примеры:**
```kotlin
// Nullable переменные
var nullable: String? = "Hello"
nullable = null  // OK

// Ненулевые переменные
var nonNullable: String = "Hello"
nonNullable = null  // Ошибка компиляции!
```

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-kotlin-operator-overloading--kotlin--medium]]
- [[q-launch-vs-async--kotlin--easy]]
- [[q-coroutine-job-lifecycle--kotlin--medium]]

---
id: lang-075
title: "Kotlin Safe Cast / Безопасное приведение типов в Kotlin"
aliases: [Kotlin Safe Cast, Безопасное приведение типов в Kotlin]
topic: programming-languages
subtopics: [null-safety, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-class-initialization-order--kotlin--medium, q-variance-type-projections--kotlin--hard]
created: 2025-10-15
updated: 2025-10-31
tags: [as?, casting, difficulty/easy, programming-languages, safe-cast, type-conversion, type-safety]
date created: Friday, October 31st 2025, 6:32:39 pm
date modified: Saturday, November 1st 2025, 5:43:24 pm
---
# Как В Kotlin Привести Переменную Типа Any К Типу String Безопасно, Чтобы Избежать Исключения?

# Вопрос (RU)
> Как в Kotlin привести переменную типа Any к типу String безопасно, чтобы избежать исключения?

---

# Question (EN)
> How to safely cast Any to String in Kotlin to avoid exceptions?

## Ответ (RU)

Используйте **оператор безопасного приведения `as?`**, который возвращает null вместо выброса исключения, если приведение типа невозможно.

**Синтаксис:**
```kotlin
val stringValue = anyVariable as? String
```

**Сравнение:**

| Оператор | Успех | Неудача |
|----------|---------|---------|
| `as` | Возвращает приведённое значение | Выбрасывает `ClassCastException` |
| `as?` | Возвращает приведённое значение | Возвращает `null` |

**Примеры:**
```kotlin
val any: Any = "Hello"
val str1 = any as? String      // "Hello" (успех)
val str2 = any as String        // "Hello" (успех)

val number: Any = 42
val str3 = number as? String    // null (безопасно)
val str4 = number as String     // ClassCastException!

// С оператором Elvis
val result = any as? String ?: "default"
```

**Когда использовать:**
- Когда вы не уверены, что приведение будет успешным
- Когда вы хотите обработать неудачу изящно
- Чтобы избежать блоков try-catch для приведения типов

## Answer (EN)

Use the **safe cast operator `as?`**, which returns null instead of throwing an exception if the cast is not possible.

**Syntax:**
```kotlin
val stringValue = anyVariable as? String
```

**Comparison:**

| Operator | Success | Failure |
|----------|---------|---------|
| `as` | Returns casted value | Throws `ClassCastException` |
| `as?` | Returns casted value | Returns `null` |

**Examples:**
```kotlin
val any: Any = "Hello"
val str1 = any as? String      // "Hello" (success)
val str2 = any as String        // "Hello" (success)

val number: Any = 42
val str3 = number as? String    // null (safe)
val str4 = number as String     // ClassCastException!

// With Elvis operator
val result = any as? String ?: "default"
```

**When to use:**
- When you're not sure if cast will succeed
- When you want to handle failure gracefully
- To avoid try-catch blocks for casting

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

-
- [[q-variance-type-projections--kotlin--hard]]
- [[q-class-initialization-order--kotlin--medium]]

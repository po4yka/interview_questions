---
id: "20251015082237198"
title: "Kotlin Safe Cast / Безопасное приведение типов в Kotlin"
topic: computer-science
difficulty: easy
status: draft
created: 2025-10-15
tags: - as?
  - casting
  - kotlin
  - programming-languages
  - safe-cast
  - type-conversion
  - type-safety
---
# Как в Kotlin привести переменную типа Any к типу String безопасно, чтобы избежать исключения?

# Question (EN)
> How to safely cast Any to String in Kotlin to avoid exceptions?

# Вопрос (RU)
> Как в Kotlin привести переменную типа Any к типу String безопасно, чтобы избежать исключения?

---

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

## Ответ (RU)

Используйте оператор приведения типов `as?`, который возвращает null вместо выброса исключения, если приведение невозможно. Например: val stringValue = anyVariable as? String


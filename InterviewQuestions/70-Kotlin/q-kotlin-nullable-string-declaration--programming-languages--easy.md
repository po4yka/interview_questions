---
id: "20251015082237105"
title: "Kotlin Nullable String Declaration / Объявление nullable String в Kotlin"
topic: computer-science
difficulty: easy
status: draft
created: 2025-10-15
tags: - kotlin
  - null-safety
  - nullable
  - programming-languages
  - string
  - syntax
---
# Как правильно объявить переменную типа nullable String в Kotlin?

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

В Kotlin для объявления переменной типа nullable String используется оператор ?. после типа данных. Например: var name: String? = null


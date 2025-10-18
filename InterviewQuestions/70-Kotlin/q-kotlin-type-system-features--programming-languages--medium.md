---
id: 20251012-12271111157
title: "Kotlin Type System Features / Возможности системы типов Kotlin"
topic: computer-science
difficulty: medium
status: draft
created: 2025-10-15
tags:
  - data-classes
  - kotlin
  - null-safety
  - programming-languages
  - sealed-classes
  - smart-casts
  - type-inference
  - type-system
---
# Какие знаешь особенности системы типов в Kotlin?

# Question (EN)
> What Kotlin type system features do you know?

# Вопрос (RU)
> Какие знаешь особенности системы типов в Kotlin?

---

## Answer (EN)

Kotlin's type system has several powerful features:

### 1. Null Safety
Variables cannot be null by default, preventing NullPointerException:
```kotlin
var nonNull: String = "Hello"     // Cannot be null
var nullable: String? = null      // Explicitly nullable
```

### 2. Collections (Mutable vs Immutable)
Clear separation between read-only and mutable collections:
```kotlin
val list: List<String> = listOf("a", "b")           // Read-only
val mutableList: MutableList<String> = mutableListOf("a", "b")
```

### 3. Data Classes
Automatic generation of `equals()`, `hashCode()`, `toString()`:
```kotlin
data class User(val name: String, val age: Int)
```

### 4. Smart Casts
Automatic type casting after checking with `is`:
```kotlin
fun demo(x: Any) {
    if (x is String) {
        println(x.length)  // x automatically cast to String
    }
}
```

### 5. Sealed Classes
Simplified handling of limited class hierarchies:
```kotlin
sealed class Result {
    data class Success(val data: String) : Result()
    data class Error(val message: String) : Result()
}
```

### 6. Type Inference
Kotlin automatically determines variable type:
```kotlin
val x = 10        // Type inferred as Int
val name = "John" // Type inferred as String
```

These features make Kotlin code **safer, more concise, and more expressive**.

---

## Ответ (RU)

Null Safety (Безопасность null), Коллекции разделение на изменяемые и неизменяемые коллекции, Data Classes автоматическое создание методов equals hashCode и toString, Smart Casts автоматическое приведение типа после проверки с помощью is, Sealed Classes упрощают обработку ограниченных иерархий классов, Выведение типов Kotlin автоматически определяет тип переменной


---
id: 20251003141105
title: Kotlin type system features / Особенности системы типов Kotlin
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, type-system]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/653
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-type-system

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, type-system, null-safety, smart-casts, sealed-classes, data-classes, type-inference, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What Kotlin type system features do you know

# Вопрос (RU)
> Какие знаешь особенности системы типов в Kotlin

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

## Ответ (RU)

Null Safety (Безопасность null), Коллекции разделение на изменяемые и неизменяемые коллекции, Data Classes автоматическое создание методов equals hashCode и toString, Smart Casts автоматическое приведение типа после проверки с помощью is, Sealed Classes упрощают обработку ограниченных иерархий классов, Выведение типов Kotlin автоматически определяет тип переменной

---

## Follow-ups
- How do smart casts work with nullable types?
- What are reified type parameters?
- How does type inference algorithm work?

## References
- [[c-kotlin-type-system]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-java-type-differences--programming-languages--medium]]
- [[q-kotlin-null-safety--programming-languages--medium]]

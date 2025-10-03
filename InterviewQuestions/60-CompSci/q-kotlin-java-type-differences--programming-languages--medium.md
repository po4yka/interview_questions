---
id: 20251003141106
title: Kotlin vs Java type differences / Различия типов в Kotlin и Java
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, java, type-system]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/655
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-java-differences
  - c-type-systems

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, java, types, comparison, null-safety, type-inference, collections, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> How do Kotlin types differ from Java types

# Вопрос (RU)
> Чем типы в Kotlin отличаются от типов в Java

---

## Answer (EN)

| Feature | Kotlin | Java |
|---------|--------|------|
| **Null Safety** | Variables cannot be null by default (`String` vs `String?`) | All objects can be null |
| **Collections** | Clear separation: `List` vs `MutableList` | No distinction (all mutable) |
| **Data Classes** | Automatic method generation with `data class` | Manual implementation required |
| **Type Inference** | Extensive: `val x = 10` | Limited (local variables with `var`) |
| **Smart Casts** | Automatic after `is` check | Explicit cast after `instanceof` |
| **Primitive Types** | No primitives (unified type system) | Separate primitives (`int`) and wrappers (`Integer`) |

**Examples:**

```kotlin
// Kotlin
val name: String = "John"        // Cannot be null
val nullable: String? = null     // Explicitly nullable
val list = listOf(1, 2, 3)       // Immutable
val x = 10                       // Type inferred

if (obj is String) {
    println(obj.length)          // Auto-cast
}
```

```java
// Java
String name = "John";             // Can be null
String nullable = null;           // No distinction
List<Integer> list = List.of(1, 2, 3); // Can be modified with reflection
int x = 10;                       // Must specify type

if (obj instanceof String) {
    println(((String) obj).length()); // Explicit cast
}
```

**Key differences:**
1. **Kotlin**: Null safety by default
2. **Kotlin**: Immutable/mutable collections distinction  
3. **Kotlin**: Auto-generated methods for data classes
4. **Kotlin**: Better type inference
5. **Kotlin**: Smart casts after type checks

## Ответ (RU)

В Kotlin по умолчанию переменные не могут быть null, в отличие от Java где все объекты могут быть null...

---

## Follow-ups
- How does Kotlin handle primitive types internally?
- What are platform types?
- How to interop between Kotlin and Java types?

## References
- [[c-kotlin-java-differences]]
- [[c-type-systems]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-type-system-features--programming-languages--medium]]
- [[q-kotlin-null-safety--programming-languages--medium]]

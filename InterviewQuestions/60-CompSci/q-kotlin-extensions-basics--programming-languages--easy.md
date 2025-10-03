---
id: 20251003141110
title: Kotlin extensions basics / Основы расширений в Kotlin
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, extensions]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/765
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-extensions

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, extensions, extension-functions, difficulty/easy, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What are Extensions?

# Вопрос (RU)
> Что такое Extensions?

---

## Answer (EN)

**Extensions** are functionality that allows **adding new capabilities to existing classes** without modifying their source code or using inheritance.

**Key characteristics:**

- Add methods/properties to existing classes
- No need to inherit or modify original class
- Resolved statically (compile-time)
- Cannot access private members

**Extension functions:**
```kotlin
// Add function to String class
fun String.addExclamation(): String {
    return this + "!"
}

// Usage
val result = "Hello".addExclamation()  // "Hello!"
```

**Extension properties:**
```kotlin
// Add property to String
val String.firstChar: Char
    get() = this[0]

// Usage
val first = "Hello".firstChar  // 'H'
```

**Why extensions are useful:**

1. **Extend existing classes**: Add utility methods to standard library classes
2. **No inheritance needed**: Works with final classes
3. **Better code organization**: Group related functions
4. **DSL creation**: Build domain-specific languages

**Example with standard library:**
```kotlin
// These are extension functions!
val list = listOf(1, 2, 3)
list.filter { it > 1 }    // Extension on List
list.map { it * 2 }       // Extension on List

"hello".capitalize()       // Extension on String
```

**Limitations:**
- Cannot override existing members
- Resolved statically (not polymorphic)
- Cannot access private members of the class

## Ответ (RU)

Термин 'Extensions' используется для обозначения функциональности, которая позволяет добавлять новые возможности к существующим классам без изменения их исходного кода.

---

## Follow-ups
- How are extensions implemented under the hood?
- Can extensions be overridden?
- What are extension receivers?

## References
- [[c-kotlin-extensions]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-extensions-overview--programming-languages--easy]]
- [[q-extension-properties--programming-languages--medium]]

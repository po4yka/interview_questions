---
id: 20251003141102
title: All Kotlin classes inherit from Any / Наследование от Any в Kotlin
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, type-system]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/544
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
tags: [kotlin, any, inheritance, type-hierarchy, object, difficulty/easy, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> All Kotlin classes inherit from Any

# Вопрос (RU)
> Все классы Kotlin наследуются от Any

---

## Answer (EN)

In Kotlin, **all classes by default inherit from the `Any` class**. This class is the root (base) class for all other classes in Kotlin. It is analogous to the `Object` class in Java.

**Key points:**

- **Any** is the supertype of all non-nullable types
- Analogous to Java's `Object` class
- Every class implicitly extends `Any` (even without explicit declaration)

**Any provides three methods:**
```kotlin
open class Any {
    public open operator fun equals(other: Any?): Boolean
    public open fun hashCode(): Int
    public open fun toString(): String
}
```

**Example:**
```kotlin
class MyClass  // Implicitly extends Any

val obj: Any = MyClass()  // Can assign to Any
obj.toString()            // Methods from Any available
obj.equals(obj)
obj.hashCode()
```

**Type hierarchy:**
```
Any (root)
├── String
├── Int
├── List<T>
└── YourCustomClass
```

**Note**: For nullable types, the root is `Any?`

## Ответ (RU)

В Kotlin все классы по умолчанию наследуются от класса Any. Этот класс является корневым (базовым) классом для всех других классов в Kotlin. Он аналогичен классу Object в Java.

---

## Follow-ups
- What's the difference between Any and Any??
- How does Any differ from Object in Java?
- Can you override methods from Any?

## References
- [[c-kotlin-type-system]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-any-unit-nothing--programming-languages--medium]]
- [[q-kotlin-any-class-methods--programming-languages--medium]]

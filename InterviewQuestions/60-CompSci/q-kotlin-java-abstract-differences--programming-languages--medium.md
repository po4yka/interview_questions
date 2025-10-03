---
id: 20251003141104
title: Abstract classes in Java vs Kotlin / Абстрактные классы в Java и Kotlin
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, java, oop]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/613
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-java-differences
  - c-abstract-classes

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, java, abstract, oop, inheritance, open, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What is the main difference between Java and Kotlin regarding abstract classes and methods

# Вопрос (RU)
> Какое главное отличие между Java и Kotlin касательно абстрактных классов и методов

---

## Answer (EN)

The main difference is how **overriding** is handled:

### Java
- **Abstract methods** implicitly allow overriding (no keyword needed)
- **Non-abstract methods** are final by default (cannot override without explicitly making them non-final)
- Must explicitly mark as `abstract` or `final`

```java
abstract class Animal {
    abstract void makeSound();     // Can override (implicit)
    void sleep() { }               // Cannot override (final by default)
    
    // Must explicitly allow overriding:
    public void eat() { }          // Still final!
}
```

### Kotlin
- **Abstract members** are `open` by default (can be overridden)
- **Non-abstract members** are `final` by default (must use `open` to allow overriding)
- More explicit about inheritance intentions

```kotlin
abstract class Animal {
    abstract fun makeSound()       // Can override (open by default)
    fun sleep() { }                // Cannot override (final by default)
    
    open fun eat() { }             // Must use 'open' to allow overriding
}
```

**Comparison table:**

| Member type | Java | Kotlin |
|-------------|------|--------|
| Abstract method | Implicitly overridable | `open` by default |
| Regular method | Final unless overridden | `final` unless marked `open` |
| Abstract class | Can be extended | Can be extended |

**Philosophy difference:**
- **Java**: Abstract methods are automatically overridable
- **Kotlin**: Explicit `open` keyword required for non-abstract methods

This makes Kotlin's inheritance model **more explicit and intentional**.

## Ответ (RU)

В Kotlin абстрактные классы и методы по умолчанию open, что позволяет их переопределять без явного указания модификатора open. В Java абстрактные методы всегда подразумевают переопределение, а обычные методы должны быть явно помечены abstract или final.

---

## Follow-ups
- Why did Kotlin choose final by default?
- What is the 'open' keyword?
- When should you use abstract vs interface?

## References
- [[c-kotlin-java-differences]]
- [[c-abstract-classes]]
- [[moc-kotlin]]

## Related Questions
- [[q-abstract-class-purpose--programming-languages--medium]]
- [[q-interface-vs-abstract-class--programming-languages--medium]]

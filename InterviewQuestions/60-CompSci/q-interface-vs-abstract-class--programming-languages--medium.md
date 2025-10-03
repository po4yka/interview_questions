---
id: 20251003140908
title: Interface vs Abstract Class / Интерфейс против абстрактного класса
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, oop]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/208
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-oop
  - c-kotlin-classes

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, interface, abstract-class, oop, inheritance, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What is an interface and how does it differ from abstract class

# Вопрос (RU)
> Что такое interface и чем он отличается от абстрактного класса

---

## Answer (EN)

**Interface** defines a set of abstract methods that a class must implement. Interfaces can contain default method implementations (in Kotlin).

**Abstract class** cannot be instantiated itself and can contain both abstract methods and methods with implementation.

**Main differences:**

| Aspect | Interface | Abstract Class |
|--------|-----------|----------------|
| **Multiple inheritance** | Class can implement multiple interfaces | Class can inherit only one abstract class |
| **Method implementation** | Can have default implementations | Can contain full method implementations |
| **Fields/state** | Cannot contain state (only properties with custom getters) | Can contain fields and state |
| **Constructors** | Cannot have constructors | Can have constructors |
| **When to use** | Define behavior contract | Share code among related classes |

**Example:**
```kotlin
interface Animal {
    fun eat()
}

abstract class Mammal {
    abstract fun breathe()
    fun sleep() = println("Sleeping")
}

class Dog : Mammal(), Animal {
    override fun eat() = println("Dog eating")
    override fun breathe() = println("Dog breathing")
}
```

## Ответ (RU)

Interface определяет набор абстрактных методов которые должен реализовать класс...

---

## Follow-ups
- Can interfaces have constructors in Kotlin?
- What are functional interfaces (SAM)?
- When should you prefer interface over abstract class?

## References
- [[c-oop]]
- [[c-kotlin-classes]]
- [[moc-kotlin]]

## Related Questions
- [[q-abstract-class-purpose--programming-languages--medium]]

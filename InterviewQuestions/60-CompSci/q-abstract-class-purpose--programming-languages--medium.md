---
id: 20251003140909
title: Abstract class purpose / Назначение абстрактного класса
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, oop]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/225
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
tags: [kotlin, abstract-class, oop, inheritance, template-method, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What is an abstract class and what is it used for

# Вопрос (RU)
> Что такое абстрактный класс и для чего он используется

---

## Answer (EN)

Abstract class represents a class that cannot be instantiated directly. It's intended for use as a base class from which other classes will inherit.

**Why it's needed:**

1. **Defining common template**: Allows defining common template for a group of subclasses. Can provide default implementation for some methods and leave others abstract for subclasses to implement

2. **Encapsulating common properties and methods**: Used to encapsulate attributes and methods that should be common to all subclasses. Reduces code duplication and improves modularity

3. **Enforcing method implementation**: Can require that all derived classes implement certain methods, guaranteeing consistent interface regardless of subclass implementation

**Features:**
- **Non-instantiability**: Cannot create instances directly
- **Abstract methods**: Have no implementation, must be implemented in subclasses
- **Can contain implementation**: Can also have fully implemented methods
- **Can have state**: Can contain fields and properties

**Example:**
```kotlin
abstract class Shape {
    abstract fun area(): Double
    
    fun describe() {
        println("Area: ${area()}")
    }
}

class Circle(val radius: Double) : Shape() {
    override fun area() = Math.PI * radius * radius
}
```

## Ответ (RU)

Абстрактный класс представляет собой класс, который не может быть инстанцирован напрямую...

---

## Follow-ups
- When should you use abstract class vs interface?
- Can abstract classes have constructors?
- What is the Template Method pattern?

## References
- [[c-oop]]
- [[c-kotlin-classes]]
- [[moc-kotlin]]

## Related Questions
- [[q-interface-vs-abstract-class--programming-languages--medium]]

---
id: cs-017
title: "Abstract Class Purpose / Назначение абстрактных классов"
aliases: ["Abstract Class Purpose", "Назначение абстрактных классов"]
topic: cs
subtopics: [oop, inheritance, abstraction]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [q-interface-vs-abstract-class--programming-languages--medium, q-oop-principles-deep-dive--computer-science--medium, q-inheritance-vs-composition--oop--medium]
created: 2025-10-15
updated: 2025-01-25
tags: [abstract-class, inheritance, kotlin, oop, template-method, difficulty/medium]
sources: [https://kotlinlang.org/docs/inheritance.html]
---

# Вопрос (RU)
> Что такое абстрактный класс и для чего он используется?

# Question (EN)
> What is an abstract class and what is it used for?

---

## Ответ (RU)

**Теория абстрактных классов:**
Abstract class - класс, который не может быть инстанцирован напрямую. Предназначен для использования как базовый класс, от которого будут наследоваться другие классы. Позволяет определить общий шаблон для группы подклассов, предоставляя реализацию по умолчанию для одних методов и оставляя другие абстрактными.

**Ключевые особенности:**
- Неинстанцируемость - нельзя создавать экземпляры напрямую
- Абстрактные методы - не имеют реализации, должны быть реализованы в подклассах
- Может содержать реализацию - может иметь полностью реализованные методы
- Может иметь состояние - может содержать поля и свойства

**Почему нужен:**
1. **Определение общего шаблона**: Общий шаблон для группы подклассов
2. **Инкапсуляция общих свойств**: Инкапсулирует атрибуты и методы, общие для всех подклассов
3. **Принуждение к реализации**: Требует реализации определённых методов, гарантируя согласованный интерфейс

**Применение:**
```kotlin
// ✅ Абстрактный класс для геометрических фигур
abstract class Shape {
    abstract fun area(): Double

    fun describe() {
        println("Area: ${area()}")
    }
}

class Circle(val radius: Double) : Shape() {
    override fun area() = Math.PI * radius * radius
}

class Rectangle(val width: Double, val height: Double) : Shape() {
    override fun area() = width * height
}
```

---

## Answer (EN)

**Abstract Class Theory:**
Abstract class is a class that cannot be instantiated directly. It's intended for use as a base class from which other classes will inherit. Allows defining common template for a group of subclasses, providing default implementation for some methods and leaving others abstract.

**Key Features:**
- Non-instantiability - Cannot create instances directly
- Abstract methods - Have no implementation, must be implemented in subclasses
- Can contain implementation - Can also have fully implemented methods
- Can have state - Can contain fields and properties

**Why it's needed:**
1. **Defining common template**: Common template for a group of subclasses
2. **Encapsulating common properties**: Encapsulates attributes and methods common to all subclasses
3. **Enforcing method implementation**: Requires certain methods to be implemented, guaranteeing consistent interface

**Application:**
```kotlin
// ✅ Abstract class for geometric shapes
abstract class Shape {
    abstract fun area(): Double

    fun describe() {
        println("Area: ${area()}")
    }
}

class Circle(val radius: Double) : Shape() {
    override fun area() = Math.PI * radius * radius
}

class Rectangle(val width: Double, val height: Double) : Shape() {
    override fun area() = width * height
}
```

## Follow-ups

- When to use abstract class vs interface?
- Template Method Pattern with abstract classes?
- Abstract class state vs interface stateless design?

## References

- [[c-data-structures]]
- [[c-oop-fundamentals]]

## Related Questions

### Prerequisites (Easier)
- [[q-inheritance-vs-composition--oop--medium]] - Inheritance concepts
- [[q-oop-principles-deep-dive--computer-science--medium]] - OOP fundamentals

### Related (Medium)
- [[q-interface-vs-abstract-class--programming-languages--medium]] - When to use interface vs abstract class

### Advanced (Harder)
- [[q-template-method-pattern--design-patterns--medium]] - Template Method pattern

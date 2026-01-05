---
id: cs-017
title: "Abstract Class Purpose / Назначение абстрактных классов"
aliases: ["Abstract Class Purpose", "Назначение абстрактных классов"]
topic: cs
subtopics: [abstraction, inheritance, oop]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-computer-science, c-inheritance]
created: 2025-10-15
updated: 2025-11-11
tags: [abstract-class, difficulty/medium, inheritance, oop, template-method]
sources: ["https://en.wikipedia.org/wiki/Abstract_type"]

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
// Абстрактный класс для геометрических фигур
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

## Дополнительные Вопросы (RU)

- Когда использовать абстрактный класс, а когда интерфейс?
- Паттерн Template Method с абстрактными классами?
- Состояние в абстрактных классах vs stateless-дизайн интерфейсов?

## Ссылки (RU)

- [[c-data-structures]]
- [[c-computer-science]]

## Связанные Вопросы (RU)

### Предварительные (проще)
- [[q-inheritance-vs-composition--cs--medium]] - концепции наследования

### Смежные (средней сложности)
- [[q-abstract-class-vs-interface--kotlin--medium]] - когда использовать интерфейс vs абстрактный класс

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

**`Application`:**
```kotlin
// Abstract class for geometric shapes
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
- [[c-computer-science]]

## Related Questions

### Prerequisites (Easier)
- [[q-inheritance-vs-composition--cs--medium]] - Inheritance concepts

### Related (Medium)
- [[q-abstract-class-vs-interface--kotlin--medium]] - When to use interface vs abstract class

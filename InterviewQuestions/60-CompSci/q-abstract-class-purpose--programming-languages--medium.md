---
id: "20251015082237102"
title: "Abstract Class Purpose / Назначение абстрактных классов"
topic: computer-science
difficulty: medium
status: draft
created: 2025-10-15
tags: - abstract-class
  - inheritance
  - kotlin
  - oop
  - programming-languages
  - template-method
---
# Что такое абстрактный класс и для чего он используется?

# Question (EN)
> What is an abstract class and what is it used for?

# Вопрос (RU)
> Что такое абстрактный класс и для чего он используется?

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

---

## Ответ (RU)

Абстрактный класс представляет собой класс, который не может быть инстанцирован напрямую. Он предназначен для использования в качестве базового класса, от которого будут наследоваться другие классы.

**Зачем он нужен:**

1. **Определение общего шаблона**: Позволяет определить общий шаблон для группы подклассов. Может предоставлять реализацию по умолчанию для некоторых методов и оставлять другие абстрактными для реализации в подклассах

2. **Инкапсуляция общих свойств и методов**: Используется для инкапсуляции атрибутов и методов, которые должны быть общими для всех подклассов. Уменьшает дублирование кода и улучшает модульность

3. **Принуждение к реализации методов**: Может требовать, чтобы все производные классы реализовали определенные методы, гарантируя согласованный интерфейс независимо от реализации подкласса

**Особенности:**
- **Неинстанцируемость**: Нельзя создавать экземпляры напрямую
- **Абстрактные методы**: Не имеют реализации, должны быть реализованы в подклассах
- **Может содержать реализацию**: Может также иметь полностью реализованные методы
- **Может иметь состояние**: Может содержать поля и свойства

**Пример:**
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


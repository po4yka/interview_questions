---
tags:
  - abstract-class
  - inheritance
  - kotlin
  - oop
  - programming-languages
  - template-method
difficulty: medium
status: reviewed
---

# Что такое абстрактный класс и для чего он используется?

**English**: What is an abstract class and what is it used for?

## Answer

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

## Ответ

Абстрактный класс представляет собой класс, который не может быть инстанцирован напрямую...


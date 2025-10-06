---
tags:
  - abstract-class
  - inheritance
  - interface
  - kotlin
  - oop
  - programming-languages
difficulty: medium
---

# Что такое interface и чем он отличается от абстрактного класса?

**English**: What is an interface and how does it differ from abstract class?

## Answer

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

## Ответ

Interface определяет набор абстрактных методов которые должен реализовать класс...


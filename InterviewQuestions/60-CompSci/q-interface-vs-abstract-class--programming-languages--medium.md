---
tags:
  - abstract-class
  - inheritance
  - interface
  - kotlin
  - oop
  - programming-languages
difficulty: medium
status: draft
---

# Что такое interface и чем он отличается от абстрактного класса?

# Question (EN)
> What is an interface and how does it differ from abstract class?

# Вопрос (RU)
> Что такое interface и чем он отличается от абстрактного класса?

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

---

## Ответ (RU)

**Interface** определяет набор абстрактных методов, которые должен реализовать класс. Интерфейсы могут содержать реализации методов по умолчанию (в Kotlin).

**Абстрактный класс** не может быть инстанциирован сам по себе и может содержать как абстрактные методы, так и методы с реализацией.

**Основные различия:**

| Аспект | Interface | Абстрактный класс |
|--------|-----------|-------------------|
| **Множественное наследование** | Класс может реализовывать несколько интерфейсов | Класс может наследовать только один абстрактный класс |
| **Реализация методов** | Может иметь реализации по умолчанию | Может содержать полные реализации методов |
| **Поля/состояние** | Не может содержать состояние (только свойства с пользовательскими геттерами) | Может содержать поля и состояние |
| **Конструкторы** | Не может иметь конструкторы | Может иметь конструкторы |
| **Когда использовать** | Определить контракт поведения | Разделить код между связанными классами |

**Пример:**
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


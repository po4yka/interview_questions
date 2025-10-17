---
id: "20251015082237184"
title: "Interface Vs Abstract Class"
topic: computer-science
difficulty: medium
status: draft
created: 2025-10-15
tags: - abstract-class
  - inheritance
  - interface
  - kotlin
  - oop
  - programming-languages
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

### Примеры использования

#### Interface - Контракт поведения

```kotlin
// Интерфейс определяет "что может делать"
interface Clickable {
    fun click()  // Абстрактный метод

    // Метод с реализацией по умолчанию (Kotlin)
    fun showClickAnimation() {
        println("Click animation")
    }
}

interface Focusable {
    fun setFocus(focused: Boolean)
    fun isFocused(): Boolean
}

// Класс может реализовывать несколько интерфейсов
class Button : Clickable, Focusable {
    private var focused = false

    override fun click() {
        println("Button clicked")
    }

    override fun setFocus(focused: Boolean) {
        this.focused = focused
    }

    override fun isFocused() = focused
}
```

#### Abstract Class - Общий базовый код

```kotlin
// Абстрактный класс определяет "что это такое" и содержит общий код
abstract class Vehicle {
    // Поля с состоянием
    protected var speed = 0
    protected var fuel = 100

    // Конструктор
    constructor(initialSpeed: Int) {
        this.speed = initialSpeed
    }

    // Абстрактный метод
    abstract fun start()

    // Конкретная реализация
    fun accelerate() {
        speed += 10
        fuel -= 1
        println("Speed: $speed, Fuel: $fuel")
    }

    // Другая конкретная реализация
    fun stop() {
        speed = 0
        println("Vehicle stopped")
    }
}

class Car : Vehicle(0) {
    override fun start() {
        println("Car engine started")
        speed = 10
    }
}

class Motorcycle : Vehicle(0) {
    override fun start() {
        println("Motorcycle started")
        speed = 5
    }
}
```

### Когда использовать что

**Используйте Interface когда:**
- Нужно определить контракт (что может делать объект)
- Класс должен иметь несколько поведений
- Различные, несвязанные классы должны реализовывать одно поведение
- Нужна множественная реализация

```kotlin
interface Serializable {
    fun serialize(): String
}

interface Comparable<T> {
    fun compareTo(other: T): Int
}

// Любой класс может быть Serializable и Comparable
class User : Serializable, Comparable<User> {
    override fun serialize() = "User data"
    override fun compareTo(other: User) = 0
}
```

**Используйте Abstract Class когда:**
- Есть общий код для разделения между связанными классами
- Нужны поля с состоянием
- Нужен конструктор
- Классы образуют иерархию "is-a"

```kotlin
abstract class Shape {
    // Общее состояние
    var color: String = "black"
    var filled: Boolean = false

    // Общий код
    fun describe() {
        println("Shape: color=$color, filled=$filled")
    }

    // Абстрактный метод для переопределения
    abstract fun calculateArea(): Double
}

class Circle(val radius: Double) : Shape() {
    override fun calculateArea() = Math.PI * radius * radius
}

class Rectangle(val width: Double, val height: Double) : Shape() {
    override fun calculateArea() = width * height
}
```

### Комбинирование

Можно комбинировать интерфейсы и абстрактные классы:

```kotlin
interface Drawable {
    fun draw()
}

interface Resizable {
    fun resize(scale: Double)
}

abstract class UIComponent {
    var x: Int = 0
    var y: Int = 0

    abstract fun render()

    fun moveTo(newX: Int, newY: Int) {
        x = newX
        y = newY
    }
}

// Наследует абстрактный класс и реализует интерфейсы
class CustomButton : UIComponent(), Drawable, Resizable {
    override fun render() {
        println("Rendering button at ($x, $y)")
    }

    override fun draw() {
        println("Drawing button")
    }

    override fun resize(scale: Double) {
        println("Resizing button by $scale")
    }
}
```

### Ключевое правило

**Interface = "can do" (может делать)**
**Abstract Class = "is a" (является)**

```kotlin
// Интерфейсы описывают способности
interface Flyable { fun fly() }
interface Swimmable { fun swim() }

// Абстрактный класс описывает сущность
abstract class Animal {
    abstract fun makeSound()
}

// Утка "является" животным и "может" летать и плавать
class Duck : Animal(), Flyable, Swimmable {
    override fun makeSound() = println("Quack")
    override fun fly() = println("Duck flying")
    override fun swim() = println("Duck swimming")
}
```


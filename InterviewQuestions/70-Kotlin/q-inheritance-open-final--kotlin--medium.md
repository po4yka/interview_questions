---
id: kotlin-232
title: "Inheritance in Kotlin: open, final, abstract, override / Наследование в Kotlin: open, final, abstract, override"
aliases: ["Inheritance in Kotlin", "Наследование в Kotlin"]
topic: kotlin
subtopics: [classes, inheritance, kotlin-features]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-class-initialization-order--kotlin--medium, q-data-class-detailed--kotlin--medium, q-delegation-by-keyword--kotlin--medium]
created: "2025-10-12"
updated: 2025-01-25
tags: [abstract, classes, difficulty/medium, inheritance, kotlin, kotlin-features, open-final]
sources: [https://kotlinlang.org/docs/inheritance.html]
date created: Sunday, October 12th 2025, 1:58:08 pm
date modified: Saturday, November 1st 2025, 5:43:26 pm
---

# Вопрос (RU)
> Как работают ключевые слова open, final, abstract и override в наследовании Kotlin?

# Question (EN)
> How do the open, final, abstract, and override keywords work in Kotlin inheritance?

---

## Ответ (RU)

**Теория наследования в Kotlin:**
В Kotlin по умолчанию все классы `final` (закрыты для наследования) - противоположность Java, где всё открыто. Это обеспечивает безопасность по умолчанию: классы нельзя наследовать без явного `open`. Для наследования требуется `open`, для переопределения методов - `override`. Абстрактные классы и методы помечаются `abstract`.

**Основные правила:**
- **final по умолчанию**: Все классы и методы закрыты для наследования
- **open**: Явно открывает класс/метод для наследования/переопределения
- **abstract**: Абстрактные классы/методы, которые должны быть реализованы
- **override**: Обязательное ключевое слово для переопределения методов

**Открытый класс и методы:**
```kotlin
// ✅ open класс может быть наследован
open class Vehicle(val brand: String) {
    // ✅ open метод может быть переопределён
    open fun start() {
        println("$brand vehicle starting")
    }

    // ❌ final метод не может быть переопределён
    fun stop() {
        println("$brand vehicle stopped")
    }
}

class Car(brand: String, val model: String) : Vehicle(brand) {
    // ✅ override обязателен для переопределения
    override fun start() {
        println("$brand $model is starting")
    }

    // ❌ нельзя переопределить stop - он final
}
```

**Абстрактные классы:**
```kotlin
// ✅ abstract класс не может быть инстанцирован
abstract class Shape {
    // ✅ abstract метод должен быть реализован в подклассе
    abstract fun area(): Double

    // ✅ Обычный метод может иметь реализацию
    fun describe() {
        println("Area: ${area()}")
    }
}

class Circle(val radius: Double) : Shape() {
    // ✅ Должен реализовать abstract метод
    override fun area(): Double = Math.PI * radius * radius
}
```

**final классы и методы:**
```kotlin
// ✅ final класс явно закрыт для наследования (по умолчанию все классы final)
final class NetworkManager {
    // ✅ final метод нельзя переопределить в подклассах
    final fun connect() {
        println("Connected")
    }
}

// ❌ Невозможно наследовать final класс
// class CustomNetworkManager : NetworkManager() { } // Ошибка!
```

**Множественное наследование интерфейсов:**
```kotlin
interface Flyable {
    fun fly()
}

interface Swimable {
    fun swim()
}

// ✅ Класс может реализовать несколько интерфейсов
class Duck : Flyable, Swimable {
    override fun fly() {
        println("Flying")
    }

    override fun swim() {
        println("Swimming")
    }
}
```

**Переопределение свойств:**
```kotlin
open class Base {
    open val value: Int = 1
    open var count: Int = 0
}

class Derived : Base() {
    // ✅ Можно переопределить val в var, но не наоборот
    override var value: Int = 10

    // ✅ Можно переопределить var
    override var count: Int = 5

    init {
        println("Value: $value, Count: $count")
    }
}
```

---

## Answer (EN)

**Kotlin Inheritance Theory:**
In Kotlin, all classes are `final` (closed for inheritance) by default - opposite of Java where everything is open. This provides safety by default: classes cannot be inherited without explicit `open`. Inheritance requires `open`, method overriding requires `override`. Abstract classes and methods are marked `abstract`.

**Core Rules:**
- **final by default**: All classes and methods are closed for inheritance
- **open**: Explicitly opens class/method for inheritance/overriding
- **abstract**: Abstract classes/methods that must be implemented
- **override**: Required keyword for method overriding

**Open Class and Methods:**
```kotlin
// ✅ open class can be inherited
open class Vehicle(val brand: String) {
    // ✅ open method can be overridden
    open fun start() {
        println("$brand vehicle starting")
    }

    // ❌ final method cannot be overridden
    fun stop() {
        println("$brand vehicle stopped")
    }
}

class Car(brand: String, val model: String) : Vehicle(brand) {
    // ✅ override required for overriding
    override fun start() {
        println("$brand $model is starting")
    }

    // ❌ cannot override stop - it's final
}
```

**Abstract Classes:**
```kotlin
// ✅ abstract class cannot be instantiated
abstract class Shape {
    // ✅ abstract method must be implemented in subclass
    abstract fun area(): Double

    // ✅ Regular method can have implementation
    fun describe() {
        println("Area: ${area()}")
    }
}

class Circle(val radius: Double) : Shape() {
    // ✅ Must implement abstract method
    override fun area(): Double = Math.PI * radius * radius
}
```

**Final Classes and Methods:**
```kotlin
// ✅ final class explicitly closed for inheritance (all classes final by default)
final class NetworkManager {
    // ✅ final method cannot be overridden in subclasses
    final fun connect() {
        println("Connected")
    }
}

// ❌ Cannot inherit final class
// class CustomNetworkManager : NetworkManager() { } // Error!
```

**Multiple Interface Implementation:**
```kotlin
interface Flyable {
    fun fly()
}

interface Swimable {
    fun swim()
}

// ✅ Class can implement multiple interfaces
class Duck : Flyable, Swimable {
    override fun fly() {
        println("Flying")
    }

    override fun swim() {
        println("Swimming")
    }
}
```

**Overriding Properties:**
```kotlin
open class Base {
    open val value: Int = 1
    open var count: Int = 0
}

class Derived : Base() {
    // ✅ Can override val to var, but not vice versa
    override var value: Int = 10

    // ✅ Can override var
    override var count: Int = 5

    init {
        println("Value: $value, Count: $count")
    }
}
```

## Follow-ups

- Why are classes final by default in Kotlin?
- When to use abstract vs interface?
- How does inheritance work with data classes?

## References

- [[c-oop-fundamentals]]
- https://kotlinlang.org/docs/inheritance.html

## Related Questions

### Prerequisites (Easier)
- [[q-kotlin-enum-classes--kotlin--easy]] - Enum classes

### Related (Medium)
- [[q-data-class-detailed--kotlin--medium]] - Data classes
- [[q-class-initialization-order--kotlin--medium]] - Class initialization
- [[q-sealed-class-sealed-interface--kotlin--medium]] - Sealed classes

### Advanced (Harder)
- [[q-delegation-by-keyword--kotlin--medium]] - Class delegation

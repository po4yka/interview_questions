---
id: kotlin-232
title: "Inheritance in Kotlin: open, final, abstract, override / Наследование в Kotlin: open, final, abstract, override"
aliases: ["Inheritance in Kotlin", "Наследование в Kotlin"]
topic: kotlin
subtopics: [inheritance, kotlin-features]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-class-initialization-order--kotlin--medium, q-data-class-detailed--kotlin--medium]
created: 2025-10-12
updated: 2025-11-10
tags: [abstract, classes, difficulty/medium, inheritance, kotlin, kotlin-features, open-final]
sources: ["https://kotlinlang.org/docs/inheritance.html"]
date created: Sunday, October 12th 2025, 1:58:08 pm
date modified: Tuesday, November 25th 2025, 8:53:51 pm
---

# Вопрос (RU)
> Как работают ключевые слова open, final, abstract и override в наследовании Kotlin?

# Question (EN)
> How do the open, final, abstract, and override keywords work in Kotlin inheritance?

---

## Ответ (RU)

**Теория наследования в Kotlin:**
В Kotlin по умолчанию все классы `final` (закрыты для наследования) — в отличие от Java, где классы по умолчанию открыты для наследования. Это обеспечивает безопасность по умолчанию: класс нельзя наследовать без явного `open` (или других специальных модификаторов, например `abstract`, `sealed`). Внутри не-`final` класса его члены (функции и свойства) по умолчанию также `final`: чтобы их можно было переопределять, нужно явно указать `open` или `abstract`. Для переопределения используется `override`. Абстрактные классы и методы помечаются `abstract`.

**Основные правила:**
- **class final по умолчанию**: Классы закрыты для наследования, если явно не указано `open` / `abstract` / `sealed` и т.п.
- **members final по умолчанию**: В открытом/абстрактном классе методы и свойства по умолчанию не переопределяемы; нужны `open` или `abstract`.
- **open**: Явно открывает класс/член для наследования/переопределения.
- **abstract**: Абстрактный класс нельзя инстанцировать, абстрактные члены обязаны быть реализованы в неабстрактных подклассах.
- **override**: Обязательное ключевое слово для переопределения открытых/абстрактных членов базового типа.
- Переопределённый член по умолчанию снова `open`, если не помечен `final`.

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

    // ❌ нельзя переопределить stop - он final по умолчанию
}
```

**Абстрактные классы:**
```kotlin
// ✅ abstract класс не может быть инстанцирован
abstract class Shape {
    // ✅ abstract метод должен быть реализован в неабстрактном подклассе
    abstract fun area(): Double

    // ✅ Обычный метод может иметь реализацию и вызывать абстрактные члены
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

**Множественная реализация интерфейсов:**
```kotlin
interface Flyable {
    fun fly()
}

interface Swimable {
    fun swim()
}

// ✅ Класс может реализовать несколько интерфейсов,
//    их абстрактные методы требуют override
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
    // ✅ Можно переопределить val как var, но не var как val
    override var value: Int = 10

    // ✅ Можно переопределить var как var
    override var count: Int = 5

    init {
        println("Value: $value, Count: $count")
    }
}
```

## Дополнительные Вопросы (RU)

- Почему классы в Kotlin по умолчанию final?
- Когда использовать `abstract` по сравнению с интерфейсом?
- Как наследование работает с `data`-классами?

## Ссылки (RU)

- [[c-kotlin]]
- https://kotlinlang.org/docs/inheritance.html

## Связанные Вопросы (RU)

### Предварительные (проще)
- [[q-kotlin-enum-classes--kotlin--easy]] - Enum-классы

### Похожие (средней сложности)
- [[q-data-class-detailed--kotlin--medium]] - Data-классы
- [[q-class-initialization-order--kotlin--medium]] - Порядок инициализации классов
- [[q-sealed-class-sealed-interface--kotlin--medium]] - Sealed-классы

### Продвинутые (сложнее)
- [[q-delegation-by-keyword--kotlin--medium]] - Делегирование классов

---

## Answer (EN)

**Kotlin Inheritance Theory:**
In Kotlin, all classes are `final` (closed for inheritance) by default — unlike Java, where classes are inheritable by default. This gives "safe by default" semantics: a class cannot be extended without an explicit `open` (or other special modifiers such as `abstract`, `sealed`). Inside a non-`final` class, its members (functions and properties) are also `final` by default: to allow overriding, they must be explicitly marked `open` or `abstract`. Overriding uses the `override` keyword. Abstract classes and members are marked with `abstract`.

**Core Rules:**
- **Classes final by default**: A class is closed for inheritance unless marked `open` / `abstract` / `sealed`, etc.
- **Members final by default**: In an open/abstract class, member functions and properties are not overridable unless marked `open` or `abstract`.
- **open**: Explicitly opens a class/member for inheritance/overriding.
- **abstract**: Abstract class cannot be instantiated; abstract members must be implemented in non-abstract subclasses.
- **override**: Required keyword for overriding open/abstract members from a supertype.
- Overridden members are `open` again by default unless explicitly marked `final`.

**Open Class and Methods:**
```kotlin
// ✅ open class can be inherited
open class Vehicle(val brand: String) {
    // ✅ open method can be overridden
    open fun start() {
        println("$brand vehicle starting")
    }

    // ❌ final method cannot be overridden (final by default)
    fun stop() {
        println("$brand vehicle stopped")
    }
}

class Car(brand: String, val model: String) : Vehicle(brand) {
    // ✅ override required for overriding
    override fun start() {
        println("$brand $model is starting")
    }

    // ❌ cannot override stop - it's final by default
}
```

**Abstract Classes:**
```kotlin
// ✅ abstract class cannot be instantiated
abstract class Shape {
    // ✅ abstract method must be implemented in a non-abstract subclass
    abstract fun area(): Double

    // ✅ Regular method can have an implementation and call abstract members
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

// ✅ Class can implement multiple interfaces;
//    their abstract methods require override
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
    // ✅ Can override val with var, but not var with val
    override var value: Int = 10

    // ✅ Can override var with var
    override var count: Int = 5

    init {
        println("Value: $value, Count: $count")
    }
}
```

## Follow-ups

- Why are classes final by default in Kotlin?
- When to use `abstract` vs interface?
- How does inheritance work with `data` classes?

## References

- [[c-kotlin]]
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

---
id: cs-002
title: "OOP Principles Deep Dive / Глубокое погружение в принципы ООП"
aliases: ["OOP Principles", "Принципы ООП"]
topic: cs
subtopics: [abstraction, encapsulation, inheritance, oop, polymorphism]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [q-clean-code-principles--software-engineering--medium, q-design-patterns-fundamentals--software-engineering--hard]
created: 2025-10-12
updated: 2025-01-25
tags: [abstraction, composition, difficulty/medium, encapsulation, inheritance, oop, polymorphism]
sources: [https://en.wikipedia.org/wiki/Object-oriented_programming]
---

# Вопрос (RU)
> Каковы четыре столпа ООП? Как работают инкапсуляция, наследование, полиморфизм и абстракция?

# Question (EN)
> What are the four pillars of OOP? How do encapsulation, inheritance, polymorphism, and abstraction work?

---

## Ответ (RU)

**Теория ООП:**
Object-Oriented Programming (ООП) - paradigm based on objects containing data and behavior. Four pillars: Encapsulation, Inheritance, Polymorphism, Abstraction. Provide structure для building maintainable, reusable code. Key concepts: IS-A vs HAS-A relationships, composition over inheritance, interfaces vs abstract classes, behavioral vs structural patterns.

**1. Инкапсуляция:**

*Теория:* Инкапсуляция - bundle data и methods что work с этими data. Hide internal details, control access (private/public). Validate state changes, maintain invariants. Allows changing internals без affecting users.

```kotlin
// ✅ Инкапсуляция с валидацией
class BankAccount(private val initialBalance: Double) {
    private var _balance: Double = initialBalance
        set(value) {
            require(value >= 0) { "Balance cannot be negative" }
            field = value
        }

    val balance: Double get() = _balance

    fun deposit(amount: Double) {
        require(amount > 0) { "Amount must be positive" }
        _balance += amount
    }

    fun withdraw(amount: Double): Boolean {
        if (amount <= 0 || amount > _balance) return false
        _balance -= amount
        return true
    }
}
```

**2. Наследование:**

*Теория:* Inheritance - создание new class от existing class. IS-A relationship, code reuse. Types: single, multi-level, hierarchical. Benefits: reuse, polymorphism base, organized hierarchy. Pitfalls: deep hierarchies, tight coupling, rigidity.

```kotlin
// ✅ Inheritance с Animal hierarchy
open class Animal(val name: String) {
    open fun makeSound() {
        println("$name makes a sound")
    }
}

class Dog(name: String) : Animal(name) {
    override fun makeSound() {
        println("$name barks: Woof!")
    }

    fun fetch() {
        println("$name fetches the ball")
    }
}

class Cat(name: String) : Animal(name) {
    override fun makeSound() {
        println("$name meows: Meow!")
    }

    fun climb() {
        println("$name climbs the tree")
    }
}

// ✅ Polymorphism в действии
fun processAnimal(animal: Animal) {
    animal.makeSound()  // Calls override method
}

val dog = Dog("Rex")
val cat = Cat("Whiskers")
processAnimal(dog)  // Dog barks
processAnimal(cat)  // Cat meows
```

**3. Полиморфизм:**

*Теория:* Polymorphism - many forms. Same interface, different implementations. Types: runtime (method overriding), compile-time (method overloading). Позволяет treat different types uniformly, increases flexibility, simplifies code. Key для polymorphism: late binding, virtual methods, interface/abstract class contracts.

```kotlin
// ✅ Polymorphism с Shape
open class Shape {
    open fun area(): Double = 0.0
    open fun draw() = println("Drawing shape")
}

class Circle(val radius: Double) : Shape() {
    override fun area(): Double = Math.PI * radius * radius
    override fun draw() = println("Drawing circle with radius $radius")
}

class Rectangle(val width: Double, val height: Double) : Shape() {
    override fun area(): Double = width * height
    override fun draw() = println("Drawing rectangle ${width}x${height}")
}

// ✅ Uniform interface
fun processShape(shape: Shape) {
    shape.draw()
    println("Area: ${shape.area()}")
}

val shapes = listOf(Circle(5.0), Rectangle(4.0, 6.0))
shapes.forEach { processShape(it) }
```

**4. Абстракция:**

*Теория:* Abstraction - hide complexity, show only essential features. Interfaces (CAN-DO), abstract classes (IS-A). Allows work с concepts без knowing implementation. Simplifies complex systems, reduces coupling, improves maintainability.

```kotlin
// ✅ Abstract class для IS-A
abstract class Employee(val name: String, val id: String) {
    abstract fun calculateSalary(): Double
    abstract val department: String

    open fun clockIn() {
        println("$name clocked in")
    }
}

class FullTimeEmployee(
    name: String, id: String, private val annualSalary: Double
) : Employee(name, id) {
    override val department: String = "Engineering"
    override fun calculateSalary(): Double = annualSalary / 12
}

class Contractor(
    name: String, id: String,
    private val hourlyRate: Double, private val hoursWorked: Double
) : Employee(name, id) {
    override val department: String = "Contract"
    override fun calculateSalary(): Double = hourlyRate * hoursWorked
}
```

**Интерфейсы:**

*Теория:* Interfaces - multiple inheritance, CAN-DO relationships. No state (abstract properties only), all methods abstract unless default implementation. Use для capabilities, contracts, decoupling.

```kotlin
// ✅ Interface для CAN-DO
interface Drawable {
    fun draw()
    fun erase() {
        println("Erasing...")
    }
}

interface Clickable {
    fun onClick()
    fun onDoubleClick() {
        println("Double clicked")
    }
}

class Button : Drawable, Clickable {
    override fun draw() = println("Drawing button")
    override fun onClick() = println("Button clicked")
}

// ✅ Usage
val button = Button()
button.draw()
button.onClick()
button.erase()
```

**Композиция vs Наследование:**

*Теория:* Composition - HAS-A relationship, more flexible than inheritance. Prefer composition для: behavior changes, flexibility, avoiding tight coupling. Inheritance для: IS-A relationships, code reuse, shared behavior.

```kotlin
// ❌ Inheritance (rigid)
open class Vehicle {
    open fun start() = println("Starting vehicle")
}

class Car : Vehicle() {
    override fun start() = println("Starting car engine")
}

class ElectricCar : Car() {  // Forced inheritance
    override fun start() = println("Starting electric motor")
}

// ✅ Composition (flexible)
interface Engine {
    fun start()
}

class GasEngine : Engine {
    override fun start() = println("Starting gas engine")
}

class ElectricMotor : Engine {
    override fun start() = println("Starting electric motor")
}

class FlexibleCar(private val engine: Engine) {  // Composition
    fun start() = engine.start()
}

// ✅ Usage
val gasCar = FlexibleCar(GasEngine())
val electricCar = FlexibleCar(ElectricMotor())
gasCar.start()      // Gas engine
electricCar.start()  // Electric motor
```

**Общие ошибки:**

**1. God Objects:**
*Теория:* God Object - class с too many responsibilities. Violates Single Responsibility Principle. Hard to maintain, test, reuse. Solution: split into focused classes, extract services, use composition.

```kotlin
// ❌ God Object
class UserManager {
    fun createUser() { }
    fun deleteUser() { }
    fun validateUser() { }
    fun authenticateUser() { }
    fun sendEmail() { }
    fun logActivity() { }
    // ... 50 more methods
}

// ✅ Single Responsibility
class UserService { fun createUser() { } fun deleteUser() { } }
class UserValidator { fun validate(user: User): Boolean { } }
class AuthService { fun authenticate(creds: Credentials): Boolean { } }
class EmailService { fun sendEmail(to: String, subject: String, body: String) { } }
```

**2. Deep Inheritance:**
*Теория:* Deep hierarchies - hard to understand, maintain, test. Multiple levels inheritance create coupling, fragile base class problem. Solution: shallow hierarchies, prefer composition, use interfaces.

```kotlin
// ❌ Deep inheritance
open class A
open class B : A()
open class C : B()
open class D : C()
open class E : D()  // Too deep

// ✅ Shallow + interfaces
interface Behavior1
interface Behavior2
interface Behavior3

class MyClass : Behavior1, Behavior2, Behavior3
```

**3. Leaky Abstractions:**
*Теория:* Leaky abstraction - exposes implementation details. Interface references specific implementation concepts. Solution: pure abstractions, hide internals, dependency inversion.

```kotlin
// ❌ Leaky abstraction
interface DataStore {
    fun save(data: String)
    fun getSQLConnection(): Connection  // Exposes SQL!
}

// ✅ Pure abstraction
interface DataStore {
    fun save(data: String)
    fun load(): String
}
```

**Ключевые выводы:**
1. Encapsulation - bundle data + methods, control access
2. Inheritance - IS-A relationship, code reuse
3. Polymorphism - same interface, different implementations
4. Abstraction - hide complexity, show essentials
5. Composition > Inheritance для flexibility
6. Interfaces для CAN-DO, Abstract classes для IS-A
7. Single Responsibility - each class does one thing
8. Avoid deep inheritance - shallow hierarchies
9. Pure abstractions - no leaky details
10. Program to interfaces - depend on abstractions

## Answer (EN)

**OOP Theory:**
Object-Oriented Programming (OOP) - paradigm based on objects containing data and behavior. Four pillars: Encapsulation, Inheritance, Polymorphism, Abstraction. Provide structure for building maintainable, reusable code. Key concepts: IS-A vs HAS-A relationships, composition over inheritance, interfaces vs abstract classes, behavioral vs structural patterns.

**1. Encapsulation:**

*Theory:* Encapsulation - bundle data and methods that work with that data. Hide internal details, control access (private/public). Validate state changes, maintain invariants. Allows changing internals without affecting users.

```kotlin
// ✅ Encapsulation with validation
class BankAccount(private val initialBalance: Double) {
    private var _balance: Double = initialBalance
        set(value) {
            require(value >= 0) { "Balance cannot be negative" }
            field = value
        }

    val balance: Double get() = _balance

    fun deposit(amount: Double) {
        require(amount > 0) { "Amount must be positive" }
        _balance += amount
    }

    fun withdraw(amount: Double): Boolean {
        if (amount <= 0 || amount > _balance) return false
        _balance -= amount
        return true
    }
}
```

**2. Inheritance:**

*Theory:* Inheritance - create new class from existing class. IS-A relationship, code reuse. Types: single, multi-level, hierarchical. Benefits: reuse, polymorphism base, organized hierarchy. Pitfalls: deep hierarchies, tight coupling, rigidity.

```kotlin
// ✅ Inheritance with Animal hierarchy
open class Animal(val name: String) {
    open fun makeSound() {
        println("$name makes a sound")
    }
}

class Dog(name: String) : Animal(name) {
    override fun makeSound() {
        println("$name barks: Woof!")
    }

    fun fetch() {
        println("$name fetches the ball")
    }
}

class Cat(name: String) : Animal(name) {
    override fun makeSound() {
        println("$name meows: Meow!")
    }

    fun climb() {
        println("$name climbs the tree")
    }
}

// ✅ Polymorphism in action
fun processAnimal(animal: Animal) {
    animal.makeSound()  // Calls override method
}

val dog = Dog("Rex")
val cat = Cat("Whiskers")
processAnimal(dog)  // Dog barks
processAnimal(cat)  // Cat meows
```

**3. Polymorphism:**

*Theory:* Polymorphism - many forms. Same interface, different implementations. Types: runtime (method overriding), compile-time (method overloading). Allows treating different types uniformly, increases flexibility, simplifies code. Key for polymorphism: late binding, virtual methods, interface/abstract class contracts.

```kotlin
// ✅ Polymorphism with Shape
open class Shape {
    open fun area(): Double = 0.0
    open fun draw() = println("Drawing shape")
}

class Circle(val radius: Double) : Shape() {
    override fun area(): Double = Math.PI * radius * radius
    override fun draw() = println("Drawing circle with radius $radius")
}

class Rectangle(val width: Double, val height: Double) : Shape() {
    override fun area(): Double = width * height
    override fun draw() = println("Drawing rectangle ${width}x${height}")
}

// ✅ Uniform interface
fun processShape(shape: Shape) {
    shape.draw()
    println("Area: ${shape.area()}")
}

val shapes = listOf(Circle(5.0), Rectangle(4.0, 6.0))
shapes.forEach { processShape(it) }
```

**4. Abstraction:**

*Theory:* Abstraction - hide complexity, show only essential features. Interfaces (CAN-DO), abstract classes (IS-A). Allows working with concepts without knowing implementation. Simplifies complex systems, reduces coupling, improves maintainability.

```kotlin
// ✅ Abstract class for IS-A
abstract class Employee(val name: String, val id: String) {
    abstract fun calculateSalary(): Double
    abstract val department: String

    open fun clockIn() {
        println("$name clocked in")
    }
}

class FullTimeEmployee(
    name: String, id: String, private val annualSalary: Double
) : Employee(name, id) {
    override val department: String = "Engineering"
    override fun calculateSalary(): Double = annualSalary / 12
}

class Contractor(
    name: String, id: String,
    private val hourlyRate: Double, private val hoursWorked: Double
) : Employee(name, id) {
    override val department: String = "Contract"
    override fun calculateSalary(): Double = hourlyRate * hoursWorked
}
```

**Interfaces:**

*Theory:* Interfaces - multiple inheritance, CAN-DO relationships. No state (abstract properties only), all methods abstract unless default implementation. Use for capabilities, contracts, decoupling.

```kotlin
// ✅ Interface for CAN-DO
interface Drawable {
    fun draw()
    fun erase() {
        println("Erasing...")
    }
}

interface Clickable {
    fun onClick()
    fun onDoubleClick() {
        println("Double clicked")
    }
}

class Button : Drawable, Clickable {
    override fun draw() = println("Drawing button")
    override fun onClick() = println("Button clicked")
}

// ✅ Usage
val button = Button()
button.draw()
button.onClick()
button.erase()
```

**Composition vs Inheritance:**

*Theory:* Composition - HAS-A relationship, more flexible than inheritance. Prefer composition for: behavior changes, flexibility, avoiding tight coupling. Inheritance for: IS-A relationships, code reuse, shared behavior.

```kotlin
// ❌ Inheritance (rigid)
open class Vehicle {
    open fun start() = println("Starting vehicle")
}

class Car : Vehicle() {
    override fun start() = println("Starting car engine")
}

class ElectricCar : Car() {  // Forced inheritance
    override fun start() = println("Starting electric motor")
}

// ✅ Composition (flexible)
interface Engine {
    fun start()
}

class GasEngine : Engine {
    override fun start() = println("Starting gas engine")
}

class ElectricMotor : Engine {
    override fun start() = println("Starting electric motor")
}

class FlexibleCar(private val engine: Engine) {  // Composition
    fun start() = engine.start()
}

// ✅ Usage
val gasCar = FlexibleCar(GasEngine())
val electricCar = FlexibleCar(ElectricMotor())
gasCar.start()      // Gas engine
electricCar.start()  // Electric motor
```

**Common Pitfalls:**

**1. God Objects:**
*Theory:* God Object - class with too many responsibilities. Violates Single Responsibility Principle. Hard to maintain, test, reuse. Solution: split into focused classes, extract services, use composition.

```kotlin
// ❌ God Object
class UserManager {
    fun createUser() { }
    fun deleteUser() { }
    fun validateUser() { }
    fun authenticateUser() { }
    fun sendEmail() { }
    fun logActivity() { }
    // ... 50 more methods
}

// ✅ Single Responsibility
class UserService { fun createUser() { } fun deleteUser() { } }
class UserValidator { fun validate(user: User): Boolean { } }
class AuthService { fun authenticate(creds: Credentials): Boolean { } }
class EmailService { fun sendEmail(to: String, subject: String, body: String) { } }
```

**2. Deep Inheritance:**
*Theory:* Deep hierarchies - hard to understand, maintain, test. Multiple levels inheritance create coupling, fragile base class problem. Solution: shallow hierarchies, prefer composition, use interfaces.

```kotlin
// ❌ Deep inheritance
open class A
open class B : A()
open class C : B()
open class D : C()
open class E : D()  // Too deep

// ✅ Shallow + interfaces
interface Behavior1
interface Behavior2
interface Behavior3

class MyClass : Behavior1, Behavior2, Behavior3
```

**3. Leaky Abstractions:**
*Theory:* Leaky abstraction - exposes implementation details. Interface references specific implementation concepts. Solution: pure abstractions, hide internals, dependency inversion.

```kotlin
// ❌ Leaky abstraction
interface DataStore {
    fun save(data: String)
    fun getSQLConnection(): Connection  // Exposes SQL!
}

// ✅ Pure abstraction
interface DataStore {
    fun save(data: String)
    fun load(): String
}
```

**Key Takeaways:**
1. Encapsulation - bundle data + methods, control access
2. Inheritance - IS-A relationship, code reuse
3. Polymorphism - same interface, different implementations
4. Abstraction - hide complexity, show essentials
5. Composition > Inheritance for flexibility
6. Interfaces for CAN-DO, Abstract classes for IS-A
7. Single Responsibility - each class does one thing
8. Avoid deep inheritance - shallow hierarchies
9. Pure abstractions - no leaky details
10. Program to interfaces - depend on abstractions

---

## Follow-ups

- What is the Liskov Substitution Principle?
- How does Kotlin's delegation work (by keyword)?
- What is the difference between association, aggregation, and composition?
- How do you design for testability in OOP?
- What is dependency inversion?

## Related Questions

### Prerequisites (Easier)
- Basic programming concepts
- Understanding of classes and objects

### Related (Same Level)
- [[q-solid-principles--software-design--medium]] - SOLID principles
- [[q-clean-code-principles--software-engineering--medium]] - Clean code

### Advanced (Harder)
- [[q-design-patterns-fundamentals--software-engineering--hard]] - Design patterns
- Advanced OOP patterns
- Functional vs OOP programming

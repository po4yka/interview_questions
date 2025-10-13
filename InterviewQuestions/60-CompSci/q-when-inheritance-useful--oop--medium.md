---
topic: architecture-patterns
subtopics: ["inheritance", "polymorphism", "encapsulation", "abstraction", "classes"]
tags:
  - oop
  - inheritance
  - is-a
  - composition
  - design-patterns
  - best-practices
  - polymorphism
difficulty: medium
status: draft
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-architecture-patterns
related_questions: []
---

# В каких случаях наследование полезно, а в каких нет?

# Question (EN)
> When is inheritance useful, and when is it not?

# Вопрос (RU)
> В каких случаях наследование полезно, а в каких нет?

---

## Answer (EN)

**Inheritance** is a powerful OOP mechanism, but it should be used carefully. Understanding **when to use** and **when to avoid** inheritance is crucial for good software design.

## When Inheritance IS Useful GOOD

### 1. Code Reuse

**Use inheritance when:** Multiple classes share common behavior and you want to avoid code duplication.

```kotlin
// - GOOD: Common behavior in base class
abstract class Shape {
    abstract fun area(): Double

    // Common behavior for all shapes
    fun describe() {
        println("This is a shape with area: ${area()}")
    }

    fun isLargerThan(other: Shape): Boolean {
        return this.area() > other.area()
    }
}

class Circle(val radius: Double) : Shape() {
    override fun area(): Double = Math.PI * radius * radius
}

class Rectangle(val width: Double, val height: Double) : Shape() {
    override fun area(): Double = width * height
}

class Triangle(val base: Double, val height: Double) : Shape() {
    override fun area(): Double = 0.5 * base * height
}

// Usage
val circle = Circle(5.0)
val rectangle = Rectangle(4.0, 6.0)

circle.describe()  // Reused from Shape
println(circle.isLargerThan(rectangle))  // Reused from Shape
```

**Benefit:** `describe()` and `isLargerThan()` are written once and reused by all shapes.

---

### 2. Class Hierarchies / Taxonomy

**Use inheritance when:** You have a clear **taxonomic hierarchy** with natural parent-child relationships.

```kotlin
// - GOOD: Clear taxonomy
abstract class Animal(val name: String) {
    abstract fun makeSound()

    fun sleep() {
        println("$name is sleeping")
    }
}

abstract class Mammal(name: String) : Animal(name) {
    fun giveBirth() {
        println("$name gives birth to live young")
    }
}

abstract class Bird(name: String) : Animal(name) {
    fun layEgg() {
        println("$name lays an egg")
    }
}

class Dog(name: String) : Mammal(name) {
    override fun makeSound() {
        println("$name barks: Woof!")
    }
}

class Cat(name: String) : Mammal(name) {
    override fun makeSound() {
        println("$name meows: Meow!")
    }
}

class Eagle(name: String) : Bird(name) {
    override fun makeSound() {
        println("$name screeches")
    }
}

// Clear hierarchy:
// Animal → Mammal → Dog, Cat
// Animal → Bird → Eagle
```

---

### 3. Polymorphism

**Use inheritance when:** You need to **treat different objects uniformly** through a common interface.

```kotlin
// - GOOD: Polymorphism
abstract class PaymentMethod {
    abstract fun processPayment(amount: Double)
}

class CreditCard(val cardNumber: String) : PaymentMethod() {
    override fun processPayment(amount: Double) {
        println("Processing $$amount via Credit Card $cardNumber")
    }
}

class PayPal(val email: String) : PaymentMethod() {
    override fun processPayment(amount: Double) {
        println("Processing $$amount via PayPal $email")
    }
}

class Bitcoin(val walletAddress: String) : PaymentMethod() {
    override fun processPayment(amount: Double) {
        println("Processing $$amount via Bitcoin $walletAddress")
    }
}

// Polymorphism: treat all payment methods uniformly
fun processOrder(paymentMethod: PaymentMethod, amount: Double) {
    println("Processing order...")
    paymentMethod.processPayment(amount)  // Different behavior based on type
    println("Order complete")
}

// Usage
val payments = listOf(
    CreditCard("1234-5678"),
    PayPal("user@example.com"),
    Bitcoin("1A2b3C4d5E6f")
)

payments.forEach { payment ->
    processOrder(payment, 100.0)  // Same interface, different implementations
}
```

---

### 4. IS-A Relationship

**Use inheritance when:** There's a clear **"IS-A" relationship** conceptually.

```kotlin
// - GOOD: Clear IS-A relationship
abstract class Vehicle(val brand: String) {
    abstract fun startEngine()
}

class Car(brand: String, val doors: Int) : Vehicle(brand) {
    override fun startEngine() {
        println("$brand car engine started")
    }
}

class Motorcycle(brand: String, val engineCC: Int) : Vehicle(brand) {
    override fun startEngine() {
        println("$brand motorcycle engine started")
    }
}

// Car IS-A Vehicle GOOD
// Motorcycle IS-A Vehicle GOOD
```

**Test:** If you can say "**X IS-A Y**" and it makes sense, inheritance is appropriate.

---

## When Inheritance IS NOT Useful BAD

### 1. No Clear IS-A Relationship

**Avoid inheritance when:** The "IS-A" relationship doesn't exist conceptually.

```kotlin
// - BAD: No IS-A relationship
class Employee(val name: String, val salary: Double)

class Car(val model: String) : Employee("", 0.0) {
    // Car IS-A Employee? No! BAD
}

// - GOOD: Use composition instead
class Car(val model: String) {
    private val owner: Employee? = null  // Car HAS-A Employee
}
```

---

### 2. Mixing Many Different Behaviors

**Avoid inheritance when:** You need to mix behaviors from multiple sources.

```kotlin
// - BAD: Can't inherit from multiple classes
class FlyingCar : Car, Airplane {  // - Multiple inheritance not allowed!
    // ...
}

// - GOOD: Use composition
class FlyingCar {
    private val carBehavior = Car()
    private val airplaneBehavior = Airplane()

    fun drive() = carBehavior.drive()
    fun fly() = airplaneBehavior.fly()
}

// - BETTER: Use interfaces
interface Drivable {
    fun drive()
}

interface Flyable {
    fun fly()
}

class FlyingCar : Drivable, Flyable {
    override fun drive() {
        println("Driving on road")
    }

    override fun fly() {
        println("Flying in air")
    }
}
```

---

### 3. Complex Class Hierarchies

**Avoid inheritance when:** The hierarchy becomes too deep or complex.

```kotlin
// - BAD: Deep, complex hierarchy
open class Entity
open class LivingEntity : Entity()
open class Animal : LivingEntity()
open class Mammal : Animal()
open class Carnivore : Mammal()
open class Feline : Carnivore()
open class BigCat : Feline()
class Lion : BigCat()  // 8 levels deep! BAD

// - GOOD: Flat hierarchy with composition
class Lion(
    private val habitat: Habitat,
    private val diet: Diet,
    private val mobility: Mobility
) {
    fun hunt() = diet.hunt()
    fun move() = mobility.move()
    fun live() = habitat.getLivingArea()
}
```

**Problems with deep hierarchies:**
- Hard to understand
- Difficult to modify
- Fragile (changes in base affect all children)
- Tight coupling

---

### 4. Implementation Inheritance (Code Smell)

**Avoid inheritance when:** You only want to reuse implementation, not establish a relationship.

```kotlin
// - BAD: Inheriting just for code reuse
class Logger {
    fun log(message: String) {
        println("[LOG] $message")
    }
}

class UserService : Logger() {  // - UserService IS-A Logger? No!
    fun createUser(name: String) {
        log("Creating user: $name")  // Just want to use log()
        // ...
    }
}

// - GOOD: Use composition
class UserService(private val logger: Logger) {
    fun createUser(name: String) {
        logger.log("Creating user: $name")
        // ...
    }
}
```

---

### 5. Rigid Design

**Avoid inheritance when:** You need flexibility and runtime behavior changes.

```kotlin
// - BAD: Fixed behavior at compile time
abstract class Weapon {
    abstract fun attack()
}

class Sword : Weapon() {
    override fun attack() {
        println("Swing sword")
    }
}

class Player(weapon: Weapon)  // Stuck with one weapon type

// - GOOD: Strategy pattern with composition
interface AttackStrategy {
    fun attack()
}

class SwordAttack : AttackStrategy {
    override fun attack() = println("Swing sword")
}

class BowAttack : AttackStrategy {
    override fun attack() = println("Shoot arrow")
}

class MagicAttack : AttackStrategy {
    override fun attack() = println("Cast spell")
}

class Player(private var attackStrategy: AttackStrategy) {
    fun attack() = attackStrategy.attack()

    // Can change strategy at runtime!
    fun changeWeapon(newStrategy: AttackStrategy) {
        attackStrategy = newStrategy
    }
}

// Usage
val player = Player(SwordAttack())
player.attack()  // "Swing sword"

player.changeWeapon(MagicAttack())
player.attack()  // "Cast spell"
```

---

## Decision Guide

### Use Inheritance When:

| - Criterion | Example |
|-------------|---------|
| **Clear IS-A relationship** | Dog IS-A Animal |
| **Shared behavior across similar classes** | All shapes can calculate area |
| **Need polymorphism** | Process different payment methods uniformly |
| **Stable, shallow hierarchy** | Animal → Mammal → Dog (3 levels) |
| **Extending framework/library classes** | Activity, Fragment, ViewModel |

### Use Composition/Interfaces When:

| - Avoid Inheritance | - Use Instead |
|---------------------|---------------|
| No IS-A relationship | Composition (HAS-A) |
| Need multiple behaviors | Interfaces + Composition |
| Deep hierarchy (>3 levels) | Flat design with composition |
| Need runtime flexibility | Strategy pattern |
| Implementation reuse only | Dependency injection |

---

## Android Examples

### - Good Use of Inheritance

```kotlin
// Framework inheritance - appropriate
class MainActivity : AppCompatActivity() {
    // MainActivity IS-A AppCompatActivity GOOD
}

class UserViewModel : ViewModel() {
    // UserViewModel IS-A ViewModel GOOD
}

class UserFragment : Fragment() {
    // UserFragment IS-A Fragment GOOD
}
```

### - Bad Use of Inheritance

```kotlin
// - BAD: No IS-A relationship
class DatabaseHelper : Context() {
    // DatabaseHelper IS-A Context? No! BAD
}

// - GOOD: Use composition
class DatabaseHelper(private val context: Context) {
    // DatabaseHelper HAS-A Context GOOD
}
```

---

## Best Practices

### - Favor Composition Over Inheritance

```kotlin
// Prefer this (composition)
class Car(private val engine: Engine)

// Over this (inheritance)
class Car : Engine()
```

### - Keep Hierarchies Shallow

```kotlin
// - GOOD: Shallow (2-3 levels max)
abstract class Animal
class Dog : Animal()

// - BAD: Too deep
abstract class A
abstract class B : A()
abstract class C : B()
abstract class D : C()
class E : D()
```

### - Program to Interfaces

```kotlin
// - Prefer interfaces for contracts
interface Drawable {
    fun draw()
}

class Circle : Drawable {
    override fun draw() { ... }
}

// Instead of abstract classes
abstract class DrawableShape {
    abstract fun draw()
}
```

---

## Summary

### When Inheritance IS Useful GOOD

1. **Code reuse** - Shared behavior across related classes
2. **Class hierarchies** - Clear taxonomic relationships
3. **Polymorphism** - Treat different objects uniformly
4. **IS-A relationship** - Conceptually makes sense

### When Inheritance IS NOT Useful BAD

1. **No IS-A relationship** - Use composition instead
2. **Mixing behaviors** - Use interfaces + composition
3. **Complex hierarchies** - Keep design flat
4. **Implementation reuse only** - Use dependency injection
5. **Need flexibility** - Use strategy/composition patterns

### Golden Rule

> **"Favor composition over inheritance"**

Use inheritance **sparingly** and only when there's a **clear, stable IS-A relationship**. For most cases, **composition and interfaces** provide more flexibility and maintainability.

---

## Ответ (RU)

Наследование полезно для:
- **Повторного использования кода** - когда классы имеют общее поведение
- **Создания иерархий классов** - чёткая таксономия (Animal → Mammal → Dog)
- **Использования полиморфизма** - обработка разных объектов через общий интерфейс
- **Отношения IS-A** - концептуально существует отношение "является" (Dog IS-A Animal)

Наследование не полезно когда:
- **Отсутствует отношение IS-A** - используйте композицию
- **Нужно смешивать много разных поведений** - используйте интерфейсы
- **Сложные иерархии классов** - держите дизайн плоским
- **Нужна только реализация** - используйте внедрение зависимостей

В таких случаях лучше использовать **композицию или интерфейсы**.

**Правило:** "Предпочитайте композицию наследованию"


---

## Related Questions

### Prerequisites (Easier)
- [[q-java-all-classes-inherit-from-object--programming-languages--easy]] - Inheritance
- [[q-kotlin-enum-classes--kotlin--easy]] - Enums

### Related (Medium)
- [[q-inheritance-vs-composition--oop--medium]] - Inheritance
- [[q-inheritance-composition-aggregation--oop--medium]] - Inheritance
- [[q-class-composition--oop--medium]] - Inheritance
- [[q-java-marker-interfaces--programming-languages--medium]] - Inheritance

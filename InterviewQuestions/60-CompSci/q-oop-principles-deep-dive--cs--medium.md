---id: cs-002
title: "OOP Principles Deep Dive / Глубокое погружение в принципы ООП"
aliases: ["OOP Principles", "Принципы ООП"]
topic: cs
subtopics: [abstraction, encapsulation, inheritance]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-architecture-patterns, c-oop-principles]
created: 2025-10-12
updated: 2025-11-11
tags: [abstraction, composition, difficulty/medium, encapsulation, inheritance, oop, polymorphism]
sources: ["https://en.wikipedia.org/wiki/Object-oriented_programming"]
anki_cards:
- slug: cs-002-0-en
  front: |
    What are the four pillars of OOP?
  back: |
    **Four OOP pillars**:
    
    1. **Encapsulation**: Bundle data + methods, control access via modifiers
    2. **Inheritance**: IS-A relationship, code reuse via class hierarchies
    3. **Polymorphism**: Same interface, different implementations
    4. **Abstraction**: Hide complexity, expose essential features
    
    **Key principle**: Prefer composition over inheritance.
  language: en
  difficulty: 0.5
  tags: [cs_oop, difficulty::medium]
- slug: cs-002-0-ru
  front: |
    Каковы четыре столпа ООП?
  back: |
    **Четыре столпа ООП**:
    
    1. **Инкапсуляция**: Объединение данных и методов, контроль доступа через модификаторы
    2. **Наследование**: Отношение IS-A, переиспользование кода через иерархии
    3. **Полиморфизм**: Один интерфейс, разные реализации
    4. **Абстракция**: Скрытие сложности, выставление только важного
    
    **Ключевой принцип**: Предпочитайте композицию наследованию.
  language: ru
  difficulty: 0.5
  tags: [cs_oop, difficulty::medium]

---
# Вопрос (RU)
> Каковы четыре столпа ООП? Как работают инкапсуляция, наследование, полиморфизм и абстракция?

# Question (EN)
> What are the four pillars of OOP? How do encapsulation, inheritance, polymorphism, and abstraction work?

---

## Ответ (RU)

**Теория ООП:**
Объектно-ориентированное программирование (ООП) — парадигма, основанная на объектах, которые объединяют данные и поведение. Четыре базовых принципа: инкапсуляция, наследование, полиморфизм, абстракция. Они задают структуру для построения поддерживаемого и переиспользуемого кода. Ключевые концепции: отношения IS-A vs HAS-A, "composition over inheritance", интерфейсы vs абстрактные классы, поведенческие vs структурные паттерны (см. [[c-architecture-patterns]]).

**1. Инкапсуляция:**

*Теория:* Инкапсуляция — объединение данных и методов, которые работают с этими данными, в один объект, с ограничением и контролем доступа к внутреннему состоянию (модификаторы доступа). Позволяет валидировать изменения состояния, поддерживать инварианты и изменять реализацию без влияния на пользователей класса.

```kotlin
// ✅ Инкапсуляция с валидацией
class BankAccount(initialBalance: Double) {
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

*Теория:* Наследование — механизм создания нового класса на основе существующего. Описывает отношение IS-A и позволяет переиспользовать код. Бывает одиночное, многоуровневое, иерархическое. Даёт базу для полиморфизма. Недостатки: глубокие иерархии, тесная связанность, хрупкие базовые классы.

```kotlin
// ✅ Наследование с иерархией Animal
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

// ✅ Полиморфизм в действии
fun processAnimal(animal: Animal) {
    animal.makeSound()  // Вызовет переопределённый метод
}

val dog = Dog("Rex")
val cat = Cat("Whiskers")
processAnimal(dog)  // Dog barks
processAnimal(cat)  // Cat meows
```

**3. Полиморфизм:**

*Теория:* Полиморфизм — "множество форм": единый интерфейс, разные реализации. В контексте ООП обычно выделяют:
- полиморфизм подтипов (runtime, через переопределение методов и позднее связывание);
- полиморфизм перегрузки (compile-time, ad-hoc, через методы с разной сигнатурой).

Он позволяет обрабатывать разные типы единообразно, повышает гибкость и упрощает код. Ключ: виртуальные методы, контракты интерфейсов/абстрактных классов, позднее связывание.

```kotlin
// ✅ Полиморфизм с Shape
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

// ✅ Единый интерфейс работы с фигурами
fun processShape(shape: Shape) {
    shape.draw()
    println("Area: ${shape.area()}")
}

val shapes = listOf(Circle(5.0), Rectangle(4.0, 6.0))
shapes.forEach { processShape(it) }
```

**4. Абстракция:**

*Теория:* Абстракция — сокрытие избыточной сложности и выделение существенных характеристик. В ООП это достигается через интерфейсы и абстрактные классы, которые задают контракты. Позволяет работать с концепциями, не зная деталей реализации, упрощает сложные системы, снижает связность и повышает поддерживаемость.

```kotlin
// ✅ Абстрактный класс для IS-A
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

*Теория:* Интерфейсы задают контракты и позволяют типам объявлять, что они "умеют" делать (CAN-DO). В Kotlin интерфейс может содержать абстрактные методы/свойства и реализации по умолчанию. Главное: интерфейсы позволяют типу реализовывать несколько таких контрактов (множественное наследование типов) и используются для задания возможностей, слабой связности и полиморфизма. Не стоит связывать интерфейсы только с "множественным наследованием реализации".

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

*Теория:* Композиция — отношение HAS-A, часто более гибкая альтернатива наследованию. Предпочтительна, когда нужно легко изменять поведение, избегать тесной связанности и хрупких иерархий. Наследование оправдано при явном IS-A и общем поведении.

```kotlin
// ❌ Наследование (жёстко)
open class Vehicle {
    open fun start() = println("Starting vehicle")
}

class Car : Vehicle() {
    override fun start() = println("Starting car engine")
}

class ElectricCar : Car() {  // Навязанное наследование
    override fun start() = println("Starting electric motor")
}

// ✅ Композиция (гибко)
interface Engine {
    fun start()
}

class GasEngine : Engine {
    override fun start() = println("Starting gas engine")
}

class ElectricMotor : Engine {
    override fun start() = println("Starting electric motor")
}

class FlexibleCar(private val engine: Engine) {  // Композиция
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
*Теория:* God Object — класс с чрезмерным числомresponsibilities. Нарушает принцип единственной ответственности, его сложно поддерживать, тестировать и переиспользовать. Решение: разбивать на специализированные классы, выносить сервисы, использовать композицию.

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

// ✅ Single Responsibility (упрощённый пример)
class UserService { fun createUser() { } fun deleteUser() { } }
class UserValidator { fun validate(user: User): Boolean { /* ... */ return true } }
class AuthService { fun authenticate(creds: Credentials): Boolean { /* ... */ return true } }
class EmailService { fun sendEmail(to: String, subject: String, body: String) { /* ... */ } }
```

**2. Глубокое наследование:**
*Теория:* Глубокие иерархии усложняют понимание, сопровождение и тестирование. Множество уровней наследования усиливает связанность и приводит к проблеме хрупкого базового класса. Решения: предпочитать неглубокие иерархии, композицию и интерфейсы.

```kotlin
// ❌ Deep inheritance
open class A
open class B : A()
open class C : B()
open class D : C()
open class E : D()  // Слишком глубоко

// ✅ Неглубокие иерархии + интерфейсы
interface Behavior1
interface Behavior2
interface Behavior3

class MyClass : Behavior1, Behavior2, Behavior3
```

**3. Текущие (leaky) абстракции:**
*Теория:* Текущая абстракция раскрывает детали реализации во внешнем контракте. Например, интерфейс, который ссылается на конкретную технологию хранения. Решение: формулировать "чистые" абстракции, скрывать детали и применять принцип инверсии зависимостей.

```kotlin
// ❌ Leaky abstraction
interface DataStore {
    fun save(data: String)
    fun getSQLConnection(): Connection  // Экспонирует конкретную технологию
}

// ✅ Pure abstraction
interface DataStore {
    fun save(data: String)
    fun load(): String
}
```

**Ключевые выводы:**
1. Encapsulation — объединяем данные и поведение, контролируем доступ.
2. Inheritance — IS-A, переиспользование кода, база для полиморфизма, но использовать осознанно.
3. Polymorphism — единый интерфейс, разные реализации (подтипы, перегрузка).
4. Abstraction — скрываем сложность, показываем существенное.
5. Composition > Inheritance для гибкости.
6. Interfaces — для CAN-DO контрактов и полиморфизма; abstract classes — для общих IS-A и частичной реализации.
7. Single Responsibility — каждый класс фокусируется на своей задаче.
8. Избегать глубокого наследования — предпочитать неглубокие иерархии.
9. Чистые абстракции — не протекают деталями реализации.
10. Program to interfaces — зависеть от абстракций, а не реализаций.

## Answer (EN)

**OOP Theory:**
Object-Oriented Programming (OOP) is a paradigm based on objects that combine data and behavior. The four core principles: Encapsulation, Inheritance, Polymorphism, Abstraction. They provide structure for building maintainable, reusable code. Key concepts: IS-A vs HAS-A relationships, composition over inheritance, interfaces vs abstract classes, behavioral vs structural patterns (see [[c-architecture-patterns]]).

**1. Encapsulation:**

*Theory:* Encapsulation is bundling data and the methods that operate on that data into a single unit, while hiding internal details via access control. It enables validation of state changes, maintaining invariants, and changing internals without affecting clients.

```kotlin
// ✅ Encapsulation with validation
class BankAccount(initialBalance: Double) {
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

*Theory:* Inheritance is creating a new class from an existing one. It models an IS-A relationship and supports code reuse and subtype polymorphism. Common forms: single, multi-level, hierarchical. Benefits: reuse, shared behavior, polymorphic APIs. Pitfalls: deep hierarchies, tight coupling, fragile base classes.

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
    animal.makeSound()  // Calls overridden method
}

val dog = Dog("Rex")
val cat = Cat("Whiskers")
processAnimal(dog)  // Dog barks
processAnimal(cat)  // Cat meows
```

**3. Polymorphism:**

*Theory:* Polymorphism means "many forms": the same interface with different implementations. In OO we distinguish primarily:
- subtype polymorphism (runtime) via method overriding and late binding;
- ad-hoc/overload polymorphism (compile-time) via methods with different signatures.

It allows treating different types uniformly, increases flexibility, and simplifies code. Key enablers: virtual methods, interface/abstract class contracts, and late binding.

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

*Theory:* Abstraction is hiding complexity and exposing only the essential features. In OO this is modeled via interfaces and abstract classes that define contracts. It allows working with concepts without knowing concrete implementations, simplifies complex systems, reduces coupling, and improves maintainability.

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

*Theory:* Interfaces define contracts and describe what a type can do (CAN-DO). In Kotlin, interfaces can declare abstract members and also provide default method implementations. Implementing multiple interfaces lets a class support multiple roles (multiple inheritance of type). They are used for capabilities, decoupling, and polymorphism. Do not confuse this with multiple inheritance of concrete implementation.

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

*Theory:* Composition is a HAS-A relationship and is often more flexible than inheritance. Prefer composition when you need to vary behavior, reduce coupling, or avoid brittle hierarchies. Use inheritance where there is a strong IS-A relationship and shared behavior.

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
*Theory:* A God Object is a class with too many responsibilities. It violates the Single Responsibility Principle and becomes hard to maintain, test, and reuse. Solution: split into focused classes, extract services, use composition.

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

// ✅ Single Responsibility (simplified example)
class UserService { fun createUser() { } fun deleteUser() { } }
class UserValidator { fun validate(user: User): Boolean { /* ... */ return true } }
class AuthService { fun authenticate(creds: Credentials): Boolean { /* ... */ return true } }
class EmailService { fun sendEmail(to: String, subject: String, body: String) { /* ... */ } }
```

**2. Deep Inheritance:**
*Theory:* Deep hierarchies are hard to understand, maintain, and test. Multiple inheritance levels increase coupling and cause fragile base class problems. Solution: prefer shallow hierarchies, composition, and interfaces.

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
*Theory:* A leaky abstraction exposes implementation details through its interface (e.g., returning technology-specific types). Solution: define pure abstractions, hide internals, and apply dependency inversion.

```kotlin
// ❌ Leaky abstraction
interface DataStore {
    fun save(data: String)
    fun getSQLConnection(): Connection  // Exposes SQL-specific detail
}

// ✅ Pure abstraction
interface DataStore {
    fun save(data: String)
    fun load(): String
}
```

**Key Takeaways:**
1. Encapsulation — bundle data and behavior, control access.
2. Inheritance — IS-A, code reuse, and a basis for polymorphism; use carefully.
3. Polymorphism — same interface, different implementations (subtype and overload polymorphism).
4. Abstraction — hide complexity, expose essentials.
5. Composition > Inheritance for flexibility.
6. Interfaces — CAN-DO contracts and polymorphic roles; abstract classes — IS-A with shared base implementation.
7. Single Responsibility — each class focuses on one reason to change.
8. Avoid deep inheritance — prefer shallow hierarchies.
9. Pure abstractions — do not leak implementation details.
10. Program to interfaces — depend on abstractions, not concretions.

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
- [[q-solid-principles--cs--medium]] - SOLID principles

### Advanced (Harder)
- Advanced OOP patterns
- Functional vs OOP programming

## References

- [[c-architecture-patterns]]
- "https://en.wikipedia.org/wiki/Object-oriented_programming"

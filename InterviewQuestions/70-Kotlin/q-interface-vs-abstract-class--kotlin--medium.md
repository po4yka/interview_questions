---
anki_cards:
- slug: q-interface-vs-abstract-class--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-interface-vs-abstract-class--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---id: kotlin-301
title: "Interface Vs Abstract Class / Интерфейс против абстрактного класса"
aliases: [Interface Vs Abstract Class, Интерфейс против абстрактного класса]
topic: kotlin
subtopics: [abstract-classes, inheritance, interfaces]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-aggregation, c-app-signing, c-backend, c-binary-search, c-binary-search-tree, c-binder, c-biometric-authentication, c-bm25-ranking, c-by-type, c-cap-theorem, c-ci-cd, c-ci-cd-pipelines, c-clean-code, c-compiler-optimization, c-compose-modifiers, c-compose-phases, c-compose-semantics, c-computer-science, c-concurrency, c-cross-platform-development, c-cross-platform-mobile, c-cs, c-data-classes, c-data-loading, c-debugging, c-declarative-programming, c-deep-linking, c-density-independent-pixels, c-dimension-units, c-dp-sp-units, c-dsl-builders, c-dynamic-programming, c-espresso-testing, c-event-handling, c-folder, c-functional-programming, c-gdpr-compliance, c-gesture-detection, c-gradle-build-cache, c-gradle-build-system, c-https-tls, c-image-formats, c-inheritance, c-jit-aot-compilation, c-kmm, c-kotlin, c-lambda-expressions, c-lazy-grid, c-lazy-initialization, c-level, c-load-balancing, c-manifest, c-memory-optimization, c-memory-profiler, c-microservices, c-multipart-form-data, c-multithreading, c-mutablestate, c-networking, c-offline-first-architecture, c-oop, c-oop-concepts, c-oop-fundamentals, c-oop-principles, c-play-console, c-play-feature-delivery, c-programming-languages, c-properties, c-real-time-communication, c-references, c-scaling-strategies, c-scoped-storage, c-security, c-serialization, c-server-sent-events, c-shader-programming, c-snapshot-system, c-specific, c-strictmode, c-system-ui, c-test-doubles, c-test-sharding, c-testing-pyramid, c-testing-strategies, c-theming, c-to-folder, c-token-management, c-touch-input, c-turbine-testing, c-two-pointers, c-ui-testing, c-ui-ux-accessibility, c-value-classes, c-variable, c-weak-references, c-windowinsets, c-xml]
created: 2024-10-15
updated: 2025-11-09
tags: [abstract-classes, difficulty/medium, inheritance, interfaces, kotlin, oop, programming-languages]
---
# Вопрос (RU)
> Что такое interface и чем он отличается от абстрактного класса?

# Question (EN)
> What is an interface and how does it differ from abstract class?

## Ответ (RU)

**Interface** определяет набор абстрактных методов (а также свойств), которые должен реализовать класс. В Kotlin интерфейсы могут содержать реализации методов по умолчанию и свойства с реализацией (например, с геттерами/сеттерами или инициализаторами).

**Абстрактный класс** не может быть инстанциирован сам по себе и может содержать как абстрактные методы, так и методы с реализацией. Как правило, используется как базовый класс с общим состоянием и поведением.

**Основные различия:**

| Аспект | Interface | Абстрактный класс |
|--------|-----------|-------------------|
| **Множественное наследование** | Класс может реализовывать несколько интерфейсов | Класс может наследовать только один абстрактный класс |
| **Реализация методов** | Может иметь реализации по умолчанию (default-методы) | Может содержать полные реализации методов |
| **Поля/состояние** | Может объявлять свойства и иметь реализацию, но обычно не используется как основной носитель состояния конкретного объекта | Может содержать поля и состояние, выступает как полноценный базовый класс |
| **Конструкторы** | Не может иметь конструкторы | Может иметь конструкторы |
| **Когда использовать** | Определить контракт поведения / набор способностей | Разделить код и состояние между связанными классами в иерархии "is-a" |

### Примеры Использования

#### Interface - Контракт Поведения

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

#### Abstract Class - Общий Базовый Код

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

### Когда Использовать Что

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

### Ключевое Правило

(эвристика)
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

## Answer (EN)

An **interface** defines a set of abstract methods and/or properties that a class must implement. In Kotlin, interfaces can contain default method implementations and properties with implementations (e.g., via accessors or initializers).

An **abstract class** cannot be instantiated by itself and can contain both abstract methods and concrete methods with implementation. It is typically used as a base class to share state and behavior.

**Main differences:**

| Aspect | Interface | Abstract Class |
|--------|-----------|----------------|
| **Multiple inheritance** | A class can implement multiple interfaces | A class can extend only one abstract (or any) class |
| **Method implementation** | Can have default implementations (default methods) | Can contain full method implementations |
| **Fields/state** | Can declare properties and hold state via their implementations, but is usually used to model capabilities/contract rather than primary object state | Can contain fields and state and is used as a full-fledged base class |
| **Constructors** | Cannot have constructors | Can have constructors |
| **When to use** | Define behavior contract / capabilities | Share code and state among related classes in an "is-a" hierarchy |

### Usage Examples

#### Interface - Behavior Contract

```kotlin
// Interface defines "what it can do"
interface Clickable {
    fun click()

    // Default implementation in Kotlin
    fun showClickAnimation() {
        println("Click animation")
    }
}

interface Focusable {
    fun setFocus(focused: Boolean)
    fun isFocused(): Boolean
}

// Class can implement multiple interfaces
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

#### Abstract Class - Shared Base Code

```kotlin
// Abstract class defines "what it is" and holds common code
abstract class Vehicle {
    // State fields
    protected var speed = 0
    protected var fuel = 100

    // Constructor
    constructor(initialSpeed: Int) {
        this.speed = initialSpeed
    }

    // Abstract method
    abstract fun start()

    // Concrete implementation
    fun accelerate() {
        speed += 10
        fuel -= 1
        println("Speed: $speed, Fuel: $fuel")
    }

    // Another concrete implementation
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

### When To Use What

Use an interface when:
- You need to define a contract (what an object can do)
- A class should have multiple capabilities
- Unrelated classes must share a behavior
- You need multiple inheritance of behavior

```kotlin
interface Serializable {
    fun serialize(): String
}

interface Comparable<T> {
    fun compareTo(other: T): Int
}

// Any class can be both Serializable and Comparable
class User : Serializable, Comparable<User> {
    override fun serialize() = "User data"
    override fun compareTo(other: User) = 0
}
```

Use an abstract class when:
- You have common code to share between related classes
- You need stateful fields
- You need a constructor
- Classes form an "is-a" hierarchy

```kotlin
abstract class Shape {
    // Shared state
    var color: String = "black"
    var filled: Boolean = false

    // Shared behavior
    fun describe() {
        println("Shape: color=$color, filled=$filled")
    }

    // Abstract method to override
    abstract fun calculateArea(): Double
}

class Circle(val radius: Double) : Shape() {
    override fun calculateArea() = Math.PI * radius * radius
}

class Rectangle(val width: Double, val height: Double) : Shape() {
    override fun calculateArea() = width * height
}
```

### Combining

Interfaces and abstract classes can be combined:

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

// Inherits abstract class and implements interfaces
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

### Key Heuristic

(heuristic)
**Interface = "can do"**
**Abstract Class = "is a"**

```kotlin
// Interfaces describe capabilities
interface Flyable { fun fly() }
interface Swimmable { fun swim() }

// Abstract class describes an entity
abstract class Animal {
    abstract fun makeSound()
}

// Duck "is an" Animal and "can" fly and swim
class Duck : Animal(), Flyable, Swimmable {
    override fun makeSound() = println("Quack")
    override fun fly() = println("Duck flying")
    override fun swim() = println("Duck swimming")
}
```

## Дополнительные Вопросы (RU)

- В чем ключевые отличия реализации интерфейсов и абстрактных классов в Java и Kotlin?
- Приведите практический сценарий на Kotlin (например, проект с разными источниками данных), где вы выберете interface вместо abstract class, и объясните почему.
- Приведите практический сценарий (например, иерархия UI-компонентов), где абстрактный класс лучше интерфейса, и какие ошибки возникают при неверном выборе.

## Follow-ups

- What are the key differences in how interfaces and abstract classes are implemented in Java vs Kotlin?
- Give a concrete practical scenario in Kotlin (for example, multiple data sources) where you would choose an interface over an abstract class, and explain why.
- Give a concrete practical scenario (for example, a UI component hierarchy) where an abstract class is preferable to an interface, and what typical mistakes occur when choosing between them.

## Ссылки (RU)

- [[c-kotlin]]
- https://kotlinlang.org/docs/interfaces.html
- https://kotlinlang.org/docs/inheritance.html

## References

- [[c-kotlin]]
- https://kotlinlang.org/docs/interfaces.html
- https://kotlinlang.org/docs/inheritance.html

## Связанные Вопросы (RU)

- [[q-abstract-class-vs-interface--kotlin--medium]]

## Related Questions

- [[q-abstract-class-vs-interface--kotlin--medium]]

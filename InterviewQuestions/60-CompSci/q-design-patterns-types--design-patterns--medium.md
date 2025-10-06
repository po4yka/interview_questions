---
tags:
  - design-patterns
  - software-design
  - gof-patterns
  - creational-patterns
  - structural-patterns
  - behavioral-patterns
difficulty: medium
---

# Types of Design Patterns

**English**: What are the main types of design patterns? Describe each category and provide examples.

## Answer

**Design Patterns (Паттерны проектирования)** - это общие, переиспользуемые решения часто встречающихся проблем в определенном контексте при проектировании программного обеспечения.

### Что такое Design Patterns?

Design patterns is a general, reusable solution to a commonly occurring problem within a given context in software design. It is not a finished design that can be transformed directly into source or machine code. Rather, it is a **description or template** for how to solve a problem that can be used in many different situations.

Design patterns are formalized best practices that the programmer can use to solve common problems when designing an application or system.

### Ключевые характеристики

Object-oriented design patterns typically show relationships and interactions between classes or objects, without specifying the final application classes or objects that are involved.

**Benefits**:
- Patterns allow developers to communicate using well-known, well understood names for software interactions
- Common design patterns can be improved over time, making them more robust than ad-hoc designs
- Provide proven development paradigms
- Speed up the development process
- Help prevent subtle issues that cause major problems

### Три основные группы паттернов

Design patterns are divided into **three fundamental groups**:

1. **Behavioral** (Поведенческие)
2. **Creational** (Порождающие)
3. **Structural** (Структурные)

## 1. Behavioral Patterns (Поведенческие)

Behavioral patterns describe interactions between objects and focus on how objects communicate with each other. They can reduce complex flow charts to mere interconnections between objects of various classes.

**Purpose**:
- Behavioral patterns are concerned with **algorithms** and the **assignment of responsibilities** between objects
- Behavioral patterns describe not just patterns of objects or classes but also the patterns of communication between them
- These patterns characterize complex control flow that is difficult to follow at run-time
- They shift your focus away from the flow of control to let you concentrate just on the way objects are interconnected
- Behavioral class patterns use inheritance to distribute behavior between classes

### Behavioral Patterns List

| Pattern | Description |
|---------|-------------|
| **Chain of Responsibility** | A way of passing a request between a chain of objects |
| **Command** | Encapsulate a command request as an object |
| **Interpreter** | A way to include language elements in a program |
| **Iterator** | Sequentially access the elements of a collection |
| **Mediator** | Defines simplified communication between classes |
| **Memento** | Capture and restore an object's internal state |
| **Observer** | A way of notifying change to a number of classes |
| **State** | Alter an object's behavior when its state changes |
| **Strategy** | Encapsulates an algorithm inside a class |
| **Template Method** | Defer the exact steps of an algorithm to a subclass |
| **Visitor** | Defines a new operation to a class without change |

### Примеры использования

```kotlin
// Observer Pattern Example
interface Observer {
    fun update(message: String)
}

class ConcreteObserver(private val name: String) : Observer {
    override fun update(message: String) {
        println("$name received: $message")
    }
}

class Subject {
    private val observers = mutableListOf<Observer>()

    fun attach(observer: Observer) {
        observers.add(observer)
    }

    fun notifyObservers(message: String) {
        observers.forEach { it.update(message) }
    }
}
```

## 2. Creational Patterns (Порождающие)

Creational patterns are used to create objects for a suitable class that serves as a solution for a problem. Generally when instances of several different classes are available.

**Purpose**:
- Creational patterns support the **creation of objects** in a system
- Creational patterns allow objects to be created in a system **without having to identify a specific class type** in the code
- So you do not have to write large, complex code to instantiate an object
- It does this by having the subclass of the class create the objects
- They are particularly useful when you are taking advantage of **polymorphism** and need to choose between different classes at runtime rather than compile time

### Creational Patterns List

| Pattern | Description |
|---------|-------------|
| **Abstract Factory** | Creates an instance of several families of classes |
| **Builder** | Separates object construction from its representation |
| **Factory Method** | Creates an instance of several derived classes |
| **Object Pool** | Avoid expensive acquisition and release of resources by recycling objects that are no longer in use |
| **Prototype** | A fully initialized instance to be copied or cloned |
| **Singleton** | A class of which only a single instance can exist |

### Примеры использования

```kotlin
// Singleton Pattern Example
object DatabaseConnection {
    init {
        println("Database initialized")
    }

    fun query(sql: String) {
        println("Executing: $sql")
    }
}

// Factory Method Pattern Example
interface Product {
    fun use()
}

class ConcreteProductA : Product {
    override fun use() = println("Using Product A")
}

class ConcreteProductB : Product {
    override fun use() = println("Using Product B")
}

abstract class Creator {
    abstract fun factoryMethod(): Product
}

class CreatorA : Creator() {
    override fun factoryMethod() = ConcreteProductA()
}
```

## 3. Structural Patterns (Структурные)

Structural patterns form larger structures from individual parts, generally of different classes. Structural patterns vary a great deal depending on what sort of structure is being created for what purpose.

**Purpose**:
- Structural patterns are concerned with how **classes and objects are composed** to form larger structures
- Structural class patterns use **inheritance** to compose interfaces or implementations
- As a simple example, consider how multiple inheritance mixes two or more classes into one
- The result is a class that combines the properties of its parent classes
- This pattern is particularly useful for making **independently developed class libraries work together**

### Structural Patterns List

| Pattern | Description |
|---------|-------------|
| **Adapter** | Match interfaces of different classes |
| **Bridge** | Separates an object's interface from its implementation |
| **Composite** | A tree structure of simple and composite objects |
| **Decorator** | Add responsibilities to objects dynamically |
| **Facade** | A single class that represents an entire subsystem |
| **Flyweight** | A fine-grained instance used for efficient sharing |
| **Proxy** | An object representing another object |

### Примеры использования

```kotlin
// Adapter Pattern Example
interface MediaPlayer {
    fun play(filename: String)
}

class Mp3Player : MediaPlayer {
    override fun play(filename: String) {
        println("Playing MP3: $filename")
    }
}

class Mp4Player {
    fun playMp4(filename: String) {
        println("Playing MP4: $filename")
    }
}

class MediaAdapter(private val mp4Player: Mp4Player) : MediaPlayer {
    override fun play(filename: String) {
        if (filename.endsWith(".mp4")) {
            mp4Player.playMp4(filename)
        }
    }
}
```

## Сравнение категорий

| Category | Focus | When to Use | Examples |
|----------|-------|-------------|----------|
| **Creational** | Object creation | When you need flexible object instantiation | Singleton, Factory, Builder |
| **Structural** | Object composition | When you need to compose objects into larger structures | Adapter, Decorator, Facade |
| **Behavioral** | Object interaction | When you need to define how objects communicate | Observer, Strategy, Command |

## Gang of Four (GoF)

The original design patterns were documented in the book **"Design Patterns: Elements of Reusable Object-Oriented Software"** by the Gang of Four (Erich Gamma, Richard Helm, Ralph Johnson, and John Vlissides) in 1994.

The book describes **23 classic design patterns** across the three categories.

## Best Practices

**When to use design patterns**:
- ✅ When facing a recurring design problem
- ✅ When you need to communicate design decisions clearly
- ✅ When you want proven solutions to common problems
- ✅ When working in a team that understands patterns

**When NOT to use**:
- ❌ Don't force patterns where they don't fit
- ❌ Don't over-engineer simple solutions
- ❌ Don't use patterns just to show off knowledge
- ❌ Don't use patterns if the team doesn't understand them

**English**: Design patterns are general, reusable solutions to commonly occurring problems in software design. They are divided into **three fundamental groups**: (1) **Behavioral** - focus on object interactions and communication (Observer, Strategy, Command, etc.), (2) **Creational** - focus on object creation mechanisms (Singleton, Factory, Builder, etc.), (3) **Structural** - focus on composing objects into larger structures (Adapter, Decorator, Facade, etc.). Patterns provide proven development paradigms, improve code communication, and speed up development. Original 23 patterns documented by Gang of Four (GoF) in 1994.

## Links

- [Software design pattern](https://en.wikipedia.org/wiki/Software_design_pattern)
- [Three Types of Design Patterns](https://www.gofpatterns.com/design-patterns/module2/three-types-design-patterns.php)
- [The Basic Design Patterns All Developers Need to Know](https://www.freecodecamp.org/news/the-basic-design-patterns-all-developers-need-to-know/)
- [Design Patterns](https://sourcemaking.com/design_patterns)

## Further Reading

- [Design Patterns: Elements of Reusable Object-Oriented Software (GoF Book)](https://en.wikipedia.org/wiki/Design_Patterns)
- [Refactoring Guru - Design Patterns](https://refactoring.guru/design-patterns)

---
*Source: Kirchhoff Android Interview Questions*

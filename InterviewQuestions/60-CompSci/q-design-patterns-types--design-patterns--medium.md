---
id: design-patterns-008
title: "Design Patterns Types / Типы паттернов проектирования"
aliases: [Design Patterns Types, Типы паттернов проектирования]
topic: design-patterns
subtopics: [behavioral-patterns, creational-patterns, structural-patterns]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-design-patterns
related: [c-design-patterns, q-observer-pattern--design-patterns--medium, q-factory-method-pattern--design-patterns--medium, q-adapter-pattern--design-patterns--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [design-patterns, gof-patterns, behavioral-patterns, creational-patterns, structural-patterns, software-design, difficulty/medium]
---

# Types of Design Patterns

# Question (EN)
> What are the main types of design patterns? Describe each category and provide examples.

# Вопрос (RU)
> Какие основные типы паттернов проектирования? Опишите каждую категорию и приведите примеры.

---

## Answer (EN)


**Design Patterns (Паттерны проектирования)** - это общие, переиспользуемые решения часто встречающихся проблем в определенном контексте при проектировании программного обеспечения.

### What Are Design Patterns?


Design patterns is a general, reusable solution to a commonly occurring problem within a given context in software design. It is not a finished design that can be transformed directly into source or machine code. Rather, it is a **description or template** for how to solve a problem that can be used in many different situations.

Design patterns are formalized best practices that the programmer can use to solve common problems when designing an application or system.

### Key Characteristics


Object-oriented design patterns typically show relationships and interactions between classes or objects, without specifying the final application classes or objects that are involved.

**Benefits**:
- Patterns allow developers to communicate using well-known, well understood names for software interactions
- Common design patterns can be improved over time, making them more robust than ad-hoc designs
- Provide proven development paradigms
- Speed up the development process
- Help prevent subtle issues that cause major problems

### Three Main Groups of Patterns


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

### Usage Examples


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

### Usage Examples


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

### Usage Examples


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

## Сравнение Категорий

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
- - When facing a recurring design problem
- - When you need to communicate design decisions clearly
- - When you want proven solutions to common problems
- - When working in a team that understands patterns

**When NOT to use**:
- - Don't force patterns where they don't fit
- - Don't over-engineer simple solutions
- - Don't use patterns just to show off knowledge
- - Don't use patterns if the team doesn't understand them

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


## Ответ (RU)

### Что Такое Паттерны Проектирования?

Паттерны проектирования — это общие, переиспользуемые решения часто встречающихся проблем в определенном контексте при проектировании программного обеспечения. Это не готовый дизайн, который можно напрямую преобразовать в исходный или машинный код. Скорее, это **описание или шаблон** решения проблемы, который можно использовать во многих различных ситуациях.

Паттерны проектирования являются формализованными лучшими практиками, которые программист может использовать для решения общих проблем при проектировании приложения или системы.

### Ключевые Характеристики

Объектно-ориентированные паттерны проектирования обычно показывают отношения и взаимодействия между классами или объектами, не уточняя конкретные классы или объекты приложения.

**Преимущества**:
- Паттерны позволяют разработчикам общаться, используя хорошо известные названия для взаимодействий в программном обеспечении
- Общие паттерны проектирования могут улучшаться со временем, делая их более надежными, чем специальные решения
- Предоставляют проверенные парадигмы разработки
- Ускоряют процесс разработки
- Помогают предотвратить тонкие проблемы, которые могут вызвать серьезные ошибки

### Три Основные Группы Паттернов

Паттерны проектирования делятся на **три фундаментальные группы**:

1. **Behavioral (Поведенческие)** - описывают взаимодействия между объектами
2. **Creational (Порождающие)** - поддерживают создание объектов
3. **Structural (Структурные)** - описывают композицию классов и объектов

## 1. Поведенческие Паттерны (Behavioral)

Поведенческие паттерны описывают взаимодействия между объектами и фокусируются на том, как объекты общаются друг с другом. Они могут упростить сложные блок-схемы до простых взаимосвязей между объектами различных классов.

**Назначение**:
- Поведенческие паттерны касаются **алгоритмов** и **распределения обязанностей** между объектами
- Описывают не только паттерны объектов или классов, но и паттерны коммуникации между ними
- Характеризуют сложный поток управления, который трудно отследить во время выполнения
- Смещают фокус с потока управления, позволяя сосредоточиться на взаимосвязях объектов

### Список Поведенческих Паттернов

| Паттерн | Описание |
|---------|----------|
| **Chain of Responsibility** | Способ передачи запроса по цепочке объектов |
| **Command** | Инкапсулирует команду как объект |
| **Interpreter** | Способ включения языковых элементов в программу |
| **Iterator** | Последовательный доступ к элементам коллекции |
| **Mediator** | Определяет упрощенную коммуникацию между классами |
| **Memento** | Захват и восстановление внутреннего состояния объекта |
| **Observer** | Способ уведомления изменений множеству классов |
| **State** | Изменение поведения объекта при изменении его состояния |
| **Strategy** | Инкапсулирует алгоритм внутри класса |
| **Template Method** | Откладывает точные шаги алгоритма подклассу |
| **Visitor** | Определяет новую операцию для класса без изменений |

### Пример Использования

```kotlin
// Пример паттерна Observer
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

## 2. Порождающие Паттерны (Creational)

Порождающие паттерны используются для создания объектов подходящего класса, который служит решением проблемы. Обычно применяются когда доступны экземпляры нескольких различных классов.

**Назначение**:
- Порождающие паттерны поддерживают **создание объектов** в системе
- Позволяют создавать объекты **без необходимости указывать конкретный тип класса** в коде
- Вам не нужно писать большой, сложный код для создания объекта
- Это достигается тем, что подкласс создает объекты
- Особенно полезны при использовании **полиморфизма** и необходимости выбора между различными классами во время выполнения

### Список Порождающих Паттернов

| Паттерн | Описание |
|---------|----------|
| **Abstract Factory** | Создает экземпляры нескольких семейств классов |
| **Builder** | Отделяет конструирование объекта от его представления |
| **Factory Method** | Создает экземпляры нескольких производных классов |
| **Object Pool** | Избегает дорогостоящего получения и освобождения ресурсов |
| **Prototype** | Полностью инициализированный экземпляр для копирования |
| **Singleton** | Класс, от которого может существовать только один экземпляр |

### Примеры Использования

```kotlin
// Пример паттерна Singleton
object DatabaseConnection {
    init {
        println("Database initialized")
    }

    fun query(sql: String) {
        println("Executing: $sql")
    }
}

// Пример паттерна Factory Method
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

## 3. Структурные Паттерны (Structural)

Структурные паттерны формируют более крупные структуры из отдельных частей, обычно различных классов. Структурные паттерны сильно различаются в зависимости от того, какая структура создается и для какой цели.

**Назначение**:
- Структурные паттерны касаются того, как **классы и объекты компонуются** для формирования более крупных структур
- Структурные паттерны классов используют **наследование** для композиции интерфейсов или реализаций
- Результат — класс, который объединяет свойства своих родительских классов
- Этот паттерн особенно полезен для **совместной работы независимо разработанных библиотек классов**

### Список Структурных Паттернов

| Паттерн | Описание |
|---------|----------|
| **Adapter** | Согласование интерфейсов различных классов |
| **Bridge** | Отделяет интерфейс объекта от его реализации |
| **Composite** | Древовидная структура простых и составных объектов |
| **Decorator** | Динамическое добавление обязанностей объектам |
| **Facade** | Один класс, представляющий всю подсистему |
| **Flyweight** | Мелкозернистый экземпляр для эффективного совместного использования |
| **Proxy** | Объект, представляющий другой объект |

### Примеры Использования

```kotlin
// Пример паттерна Adapter
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

## Сравнение Категорий

| Категория | Фокус | Когда использовать | Примеры |
|-----------|-------|-------------------|---------|
| **Creational** | Создание объектов | Когда нужно гибкое создание объектов | Singleton, Factory, Builder |
| **Structural** | Композиция объектов | Когда нужно компоновать объекты в более крупные структуры | Adapter, Decorator, Facade |
| **Behavioral** | Взаимодействие объектов | Когда нужно определить, как объекты общаются | Observer, Strategy, Command |

## Gang of Four (GoF)

Оригинальные паттерны проектирования были задокументированы в книге **"Design Patterns: Elements of Reusable Object-Oriented Software"** авторами Gang of Four (Эрих Гамма, Ричард Хелм, Ральф Джонсон и Джон Влиссидес) в 1994 году.

Книга описывает **23 классических паттерна проектирования** по трем категориям.

## Лучшие Практики

**Когда использовать паттерны проектирования**:
- Когда сталкиваетесь с повторяющейся проблемой проектирования
- Когда нужно четко передать решения по дизайну
- Когда хотите проверенные решения общих проблем
- Когда работаете в команде, которая понимает паттерны

**Когда НЕ использовать**:
- Не навязывайте паттерны там, где они не подходят
- Не усложняйте простые решения
- Не используйте паттерны только чтобы показать знания
- Не используйте паттерны, если команда их не понимает

**Резюме**: Паттерны проектирования — это общие, переиспользуемые решения часто встречающихся проблем в разработке ПО. Они разделены на **три фундаментальные группы**: (1) **Поведенческие** — фокус на взаимодействиях объектов (Observer, Strategy, Command и т.д.), (2) **Порождающие** — фокус на механизмах создания объектов (Singleton, Factory, Builder и т.д.), (3) **Структурные** — фокус на композиции объектов в более крупные структуры (Adapter, Decorator, Facade и т.д.). Паттерны предоставляют проверенные парадигмы разработки, улучшают коммуникацию в коде и ускоряют разработку. Оригинальные 23 паттерна задокументированы Gang of Four в 1994 году.


---

## Related Questions

### Prerequisites (Easier)
- [[q-singleton-pattern--design-patterns--easy]] - Singleton pattern

### Creational Patterns
- [[q-factory-method-pattern--design-patterns--medium]] - Factory Method pattern
- [[q-abstract-factory-pattern--design-patterns--medium]] - Abstract Factory pattern
- [[q-builder-pattern--design-patterns--medium]] - Builder pattern
- [[q-prototype-pattern--design-patterns--medium]] - Prototype pattern

### Structural Patterns
- [[q-adapter-pattern--design-patterns--medium]] - Adapter pattern
- [[q-decorator-pattern--design-patterns--medium]] - Decorator pattern
- [[q-facade-pattern--design-patterns--medium]] - Facade pattern
- [[q-proxy-pattern--design-patterns--medium]] - Proxy pattern
- [[q-composite-pattern--design-patterns--medium]] - Composite pattern

### Behavioral Patterns
- [[q-strategy-pattern--design-patterns--medium]] - Strategy pattern
- [[q-observer-pattern--design-patterns--medium]] - Observer pattern
- [[q-command-pattern--design-patterns--medium]] - Command pattern
- [[q-template-method-pattern--design-patterns--medium]] - Template Method pattern
- [[q-iterator-pattern--design-patterns--medium]] - Iterator pattern
- [[q-state-pattern--design-patterns--medium]] - State pattern
- [[q-chain-of-responsibility--design-patterns--medium]] - Chain of Responsibility
- [[q-mediator-pattern--design-patterns--medium]] - Mediator pattern
- [[q-memento-pattern--design-patterns--medium]] - Memento pattern

### Other Patterns
- [[q-service-locator-pattern--design-patterns--medium]] - Service Locator pattern

### Advanced Patterns (Harder)
- [[q-bridge-pattern--design-patterns--hard]] - Bridge pattern
- [[q-interpreter-pattern--design-patterns--hard]] - Interpreter pattern
- [[q-visitor-pattern--design-patterns--hard]] - Visitor pattern
- [[q-flyweight-pattern--design-patterns--hard]] - Flyweight pattern

### Architecture Patterns
- [[q-mvvm-pattern--architecture-patterns--medium]] - MVVM pattern
- [[q-mvp-pattern--architecture-patterns--medium]] - MVP pattern
- [[q-mvi-pattern--architecture-patterns--hard]] - MVI pattern

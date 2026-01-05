---
id: dp-010
title: "Design Patterns Types / Типы паттернов проектирования"
aliases: [Design Patterns Types, Типы паттернов проектирования]
topic: cs
subtopics: [software-design]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-architecture-patterns, c-computer-science]
created: 2025-10-15
updated: 2025-11-11
tags: [difficulty/medium]

---
# Вопрос (RU)
> Какие основные типы паттернов проектирования? Опишите каждую категорию и приведите примеры.

# Question (EN)
> What are the main types of design patterns? Describe each category and provide examples.

---

## Ответ (RU)

### Что Такое Паттерны Проектирования?

Паттерны проектирования — это общие, переиспользуемые решения часто встречающихся проблем в определенном контексте при проектировании программного обеспечения. Это не готовый дизайн, который можно напрямую преобразовать в исходный или машинный код. Скорее, это описание или шаблон решения проблемы, который можно использовать во многих различных ситуациях.

Паттерны проектирования являются формализованными лучшими практиками, которые программист может использовать для решения общих проблем при проектировании приложения или системы.

### Ключевые Характеристики

Объектно-ориентированные паттерны проектирования обычно показывают отношения и взаимодействия между классами или объектами, не уточняя конкретные классы или объекты приложения.

Преимущества:
- Паттерны позволяют разработчикам общаться, используя хорошо известные названия для взаимодействий в программном обеспечении
- Общие паттерны проектирования могут улучшаться со временем, делая их более надежными, чем специальные решения
- Предоставляют проверенные парадигмы разработки
- Ускоряют процесс разработки
- Помогают предотвратить тонкие проблемы, которые могут вызвать серьезные ошибки

### Три Основные Группы Паттернов

Паттерны проектирования традиционно делятся на три фундаментальные группы (в классической классификации GoF):

1. Behavioral (Поведенческие) — описывают взаимодействия между объектами
2. Creational (Порождающие) — описывают способы создания объектов
3. Structural (Структурные) — описывают композицию классов и объектов

## 1. Поведенческие Паттерны (Behavioral)

Поведенческие паттерны описывают взаимодействия между объектами и фокусируются на том, как объекты общаются друг с другом. Они часто помогают выразить сложный поток управления через понятные взаимодействия объектов вместо низкоуровневой логики условий.

Назначение:
- Касаются алгоритмов и распределения обязанностей между объектами
- Описывают не только набор объектов или классов, но и паттерны коммуникации между ними
- Помогают управлять сложным потоком управления, который трудно отследить при императивной реализации
- Смещают фокус с низкоуровневого потока управления на взаимосвязи и сотрудничество объектов
- Часть поведенческих паттернов использует наследование, но многие опираются на композицию и интерфейсы

### Список Поведенческих Паттернов

| Паттерн | Описание |
|---------|----------|
| **Chain of Responsibility** | Способ передачи запроса по цепочке обработчиков до тех пор, пока один не обработает его |
| **Command** | Инкапсулирует запрос (команду) как объект |
| **Interpreter** | Описывает представление простого языка и интерпретатор для него |
| **Iterator** | Предоставляет последовательный доступ к элементам коллекции |
| **Mediator** | Определяет объект, инкапсулирующий взаимодействия между набором объектов |
| **Memento** | Захватывает и внешне хранит внутреннее состояние объекта, не нарушая инкапсуляцию |
| **Observer** | Определяет зависимость один-ко-многим для автоматических уведомлений об изменении состояния |
| **State** | Позволяет объекту изменять поведение при изменении его внутреннего состояния |
| **Strategy** | Определяет семейство алгоритмов и делает их взаимозаменяемыми |
| **Template Method** | Определяет скелет алгоритма и делегирует реализацию шагов подклассам |
| **Visitor** | Представляет операцию над элементами объектной структуры без изменения их классов |

### Пример Использования

```kotlin
// Пример паттерна Observer (упрощённый)
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

    fun detach(observer: Observer) {
        observers.remove(observer)
    }

    fun notifyObservers(message: String) {
        observers.forEach { it.update(message) }
    }
}
```

## 2. Порождающие Паттерны (Creational)

Порождающие паттерны предоставляют различные механизмы создания объектов, которые повышают гибкость и повторное использование кода. Они помогают создавать объекты подходящим образом, часто скрывая конкретные классы от клиентского кода.

Назначение:
- Поддерживают гибкое и контролируемое создание объектов в системе
- Позволяют создавать объекты без жёсткой привязки к конкретным классам в клиентском коде (программирование к интерфейсам)
- Централизуют и инкапсулируют логику инстанцирования вместо её дублирования
- Многие из них делегируют создание объектов специализированным "создателям" (фабрики, билдеры, прототипы), а не требуют, чтобы клиенты или произвольные подклассы знали все детали
- Особенно полезны при использовании полиморфизма и выборе реализации во время выполнения

### Список Порождающих Паттернов

| Паттерн | Описание |
|---------|----------|
| **Abstract Factory** | Создаёт семейства связанных объектов без указания их конкретных классов |
| **Builder** | Отделяет процесс конструирования сложного объекта от его представления |
| **Factory Method** | Определяет интерфейс для создания объекта, позволяя подклассам выбирать класс |
| **Prototype** | Определяет типы создаваемых объектов с помощью прототипа и клонирования |
| **Singleton** | Гарантирует существование только одного экземпляра класса и глобальную точку доступа |
| **Object Pool** | (Не из оригинальных GoF) Позволяет переиспользовать набор инициализированных объектов вместо постоянного создания и уничтожения |

### Примеры Использования

```kotlin
// Пример паттерна Singleton (вопросы потокобезопасности опущены для краткости)
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

    fun operate() {
        val product = factoryMethod()
        product.use()
    }
}

class CreatorA : Creator() {
    override fun factoryMethod(): Product = ConcreteProductA()
}

class CreatorB : Creator() {
    override fun factoryMethod(): Product = ConcreteProductB()
}
```

## 3. Структурные Паттерны (Structural)

Структурные паттерны формируют более крупные структуры из отдельных частей, обычно различных классов. Они фокусируются на том, как классы и объекты компонуются для получения новой функциональности.

Назначение:
- Описывают, как классы и объекты компонуются для формирования более крупных и гибких структур
- Некоторые паттерны классов используют наследование для композиции интерфейсов или реализаций
- Многие структурные паттерны объектов опираются на композицию и делегирование для комбинирования поведения во время выполнения
- Особенно полезны для интеграции независимо разработанных библиотек и добавления функциональности без изменения существующего кода

### Список Структурных Паттернов

| Паттерн | Описание |
|---------|----------|
| **Adapter** | Согласует интерфейс класса с ожидаемым клиентами |
| **Bridge** | Отделяет абстракцию от реализации, позволяя им изменяться независимо |
| **Composite** | Компонуёт объекты в древовидные структуры для представления иерархий "часть-целое" |
| **Decorator** | Динамически добавляет объекту новые обязанности |
| **Facade** | Предоставляет унифицированный интерфейс к набору интерфейсов подсистемы |
| **Flyweight** | Использует разделяемые объекты для эффективной работы с большим числом мелких объектов |
| **Proxy** | Предоставляет суррогат или заменяющий объект для управления доступом к другому объекту |

### Примеры Использования

```kotlin
// Пример паттерна Adapter (упрощённый)
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
        } else {
            println("Формат не поддерживается этим адаптером: $filename")
        }
    }
}
```

## Сравнение Категорий

| Категория | Фокус | Когда использовать | Примеры |
|-----------|-------|-------------------|---------|
| **Creational** | Создание объектов | Когда нужно гибкое создание объектов и сокрытие конкретных типов | Singleton, Factory Method, Builder |
| **Structural** | Композиция объектов | Когда нужно компоновать объекты в более крупные и гибкие структуры | Adapter, Decorator, Facade |
| **Behavioral** | Взаимодействие объектов | Когда нужно определить или варьировать взаимодействия и распределение обязанностей | Observer, Strategy, Command |

## Gang of Four (GoF)

Оригинальный каталог паттернов проектирования был задокументирован в книге "Design Patterns: Elements of Reusable Object-Oriented Software" авторами Gang of Four (Эрих Гамма, Ричард Хелм, Ральф Джонсон и Джон Влиссидес) в 1994 году.

Книга описывает 23 классических паттерна проектирования в трёх категориях.

## Лучшие Практики

Когда использовать паттерны проектирования:
- Когда сталкиваетесь с повторяющейся проблемой проектирования
- Когда нужно чётко передать решения по дизайну
- Когда нужны проверенные решения распространённых проблем
- Когда работаете в команде, которая понимает паттерны

Когда НЕ использовать:
- Не навязывайте паттерны там, где они не подходят
- Не усложняйте простые решения
- Не используйте паттерны только чтобы продемонстрировать знания
- Не используйте паттерны, если команда их не понимает

Резюме: Паттерны проектирования — это общие, переиспользуемые решения часто встречающихся проблем в разработке ПО. В классификации GoF они разделены на три фундаментальные группы: (1) Поведенческие — фокус на взаимодействиях и распределении обязанностей между объектами (Observer, Strategy, Command и т.д.), (2) Порождающие — фокус на механизмах создания объектов (Singleton, Factory Method, Builder и т.д.), (3) Структурные — фокус на композиции объектов в более крупные структуры (Adapter, Decorator, Facade и т.д.). Паттерны предоставляют проверенные парадигмы разработки, улучшают коммуникацию в команде и могут ускорять разработку. Оригинальные 23 паттерна описаны Gang of Four в 1994 году.

---

## Answer (EN)

Design patterns are general, reusable solutions to commonly occurring problems within a given context in software design. They are not finished designs that can be transformed directly into source or machine code. Rather, they are a description or template for how to solve a problem that can be used in many different situations.

Design patterns are formalized best practices that the programmer can use to solve common problems when designing an application or system.

### Key Characteristics

Object-oriented design patterns typically show relationships and interactions between classes or objects, without specifying the final application classes or objects that are involved.

Benefits:
- Patterns allow developers to communicate using well-known, well understood names for software interactions
- Common design patterns can be improved over time, making them more robust than ad-hoc designs
- Provide proven development paradigms
- Speed up the development process
- Help prevent subtle issues that cause major problems

### Three Main Groups of Patterns

Design patterns are commonly divided into three fundamental groups (in the classic GoF classification):

1. Behavioral
2. Creational
3. Structural

## 1. Behavioral Patterns

Behavioral patterns describe interactions between objects and focus on how objects communicate with each other. They often help express complex control flows through clear collaborations between objects instead of low-level conditional logic.

Purpose:
- Concerned with algorithms and the assignment of responsibilities between objects
- Describe not just sets of objects or classes but also the patterns of communication between them
- Help manage complex control flow that is difficult to follow at run-time if expressed imperatively
- Shift focus away from the low-level flow of control to the way objects are interconnected and collaborate
- Some behavioral class patterns use inheritance to distribute behavior, while many others rely on composition and interfaces

### Behavioral Patterns List

| Pattern | Description |
|---------|-------------|
| **Chain of Responsibility** | Pass a request along a chain of handlers until one handles it |
| **Command** | Encapsulate a request as an object |
| **Interpreter** | Define a representation for a simple language and an interpreter for it |
| **Iterator** | Provide sequential access to the elements of a collection |
| **Mediator** | Define an object that encapsulates how a set of objects interact |
| **Memento** | Capture and externalize an object's internal state without violating encapsulation |
| **Observer** | Define a one-to-many dependency so that dependents are notified automatically of state changes |
| **State** | Allow an object to alter its behavior when its internal state changes |
| **Strategy** | Define a family of algorithms and make them interchangeable |
| **Template Method** | Define the skeleton of an algorithm and let subclasses redefine certain steps |
| **Visitor** | Represent an operation to be performed on elements of an object structure without modifying the classes |

### Usage Examples

```kotlin
// Observer Pattern Example (simplified)
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

    fun detach(observer: Observer) {
        observers.remove(observer)
    }

    fun notifyObservers(message: String) {
        observers.forEach { it.update(message) }
    }
}
```

## 2. Creational Patterns

Creational patterns provide various object creation mechanisms that increase flexibility and reuse of existing code. They help you create objects in a way that is appropriate to the situation, often hiding the concrete classes from client code.

Purpose:
- Support flexible, controlled creation of objects in a system
- Allow objects to be created without hard-coding concrete class types in client code (program to interfaces)
- Centralize and encapsulate the logic of instantiation
- Many delegate object creation to specialized creator objects or methods (factories, builders, prototypes)
- Useful when using polymorphism and choosing implementations at runtime

### Creational Patterns List

| Pattern | Description |
|---------|-------------|
| **Abstract Factory** | Create families of related objects without specifying their concrete classes |
| **Builder** | Separate the construction of a complex object from its representation |
| **Factory Method** | Define an interface for creating an object, letting subclasses decide which class to instantiate |
| **Prototype** | Specify the kinds of objects to create using a prototypical instance, and clone it |
| **Singleton** | Ensure a class has only one instance and provide a global access point to it |
| **Object Pool** | (Non-GoF) Reuse a set of initialized objects instead of creating and destroying them repeatedly |

### Usage Examples

```kotlin
// Singleton Pattern Example (thread-safety considerations omitted for brevity)
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

    fun operate() {
        val product = factoryMethod()
        product.use()
    }
}

class CreatorA : Creator() {
    override fun factoryMethod(): Product = ConcreteProductA()
}

class CreatorB : Creator() {
    override fun factoryMethod(): Product = ConcreteProductB()
}
```

## 3. Structural Patterns

Structural patterns form larger structures from individual parts, generally of different classes. They focus on how classes and objects are composed to obtain new functionality.

Purpose:
- Concerned with how classes and objects are composed to form larger, more flexible structures
- Some use inheritance to compose interfaces or implementations
- Many rely on composition and delegation to combine behavior at runtime
- Useful for integrating independently developed libraries and adding functionality without modifying existing code

### Structural Patterns List

| Pattern | Description |
|---------|-------------|
| **Adapter** | Convert the interface of a class into another interface clients expect |
| **Bridge** | Decouple an abstraction from its implementation so the two can vary independently |
| **Composite** | Compose objects into tree structures to represent part-whole hierarchies |
| **Decorator** | Attach additional responsibilities to an object dynamically |
| **Facade** | Provide a unified interface to a set of interfaces in a subsystem |
| **Flyweight** | Use sharing to support large numbers of fine-grained objects efficiently |
| **Proxy** | Provide a surrogate or placeholder for another object to control access to it |

### Usage Examples

```kotlin
// Adapter Pattern Example (simplified)
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
        } else {
            println("Unsupported format for this adapter: $filename")
        }
    }
}
```

## Comparison of Categories

| Category | Focus | When to Use | Examples |
|----------|-------|-------------|----------|
| **Creational** | Object creation | When you need flexible object instantiation and want to hide concrete types | Singleton, Factory Method, Builder |
| **Structural** | Object composition | When you need to compose objects into larger, flexible structures | Adapter, Decorator, Facade |
| **Behavioral** | Object interaction | When you need to define or vary how objects communicate and distribute responsibilities | Observer, Strategy, Command |

## Gang of Four (GoF)

The original catalog of design patterns was documented in the book "Design Patterns: Elements of Reusable Object-Oriented Software" by the Gang of Four (Erich Gamma, Richard Helm, Ralph Johnson, and John Vlissides) in 1994.

The book describes 23 classic design patterns across the three categories.

## Best Practices

When to use design patterns:
- When facing a recurring design problem
- When you need to communicate design decisions clearly
- When you want proven solutions to common problems
- When working in a team that understands patterns

When NOT to use:
- Don't force patterns where they don't fit
- Don't over-engineer simple solutions
- Don't use patterns just to show off knowledge
- Don't use patterns if the team doesn't understand them

Summary: Design patterns are general, reusable solutions to commonly occurring problems in software design. In the GoF classification, they are divided into three fundamental groups: (1) Behavioral — focus on object interactions and communication (Observer, Strategy, Command, etc.), (2) Creational — focus on object creation mechanisms (Singleton, Factory Method, Builder, etc.), (3) Structural — focus on composing objects into larger structures (Adapter, Decorator, Facade, etc.). Patterns provide proven development paradigms, improve communication, and can speed up development. The original 23 patterns were documented by the Gang of Four (GoF) in 1994.

---

## Related Questions

- How would you decide which pattern category to start with when refactoring a legacy system?
- Can you give an example where overusing patterns made a design worse?
- How do design patterns relate to architecture patterns (e.g., layered architecture, MVC, Clean Architecture)?

## References

- [[c-architecture-patterns]]
- [[c-computer-science]]
- [Software design pattern](https://en.wikipedia.org/wiki/Software_design_pattern)
- [Three Types of Design Patterns](https://www.gofpatterns.com/design-patterns/module2/three-types-design-patterns.php)
- [The Basic Design Patterns All Developers Need to Know](https://www.freecodecamp.org/news/the-basic-design-patterns-all-developers-need-to-know/)
- [Design Patterns](https://sourcemaking.com/design_patterns)
- [Design Patterns: Elements of Reusable Object-Oriented Software (GoF Book)](https://en.wikipedia.org/wiki/Design_Patterns)
- [Refactoring Guru - Design Patterns](https://refactoring.guru/design-patterns)

---
id: 20251012-1227111171
title: Prototype Pattern
topic: design-patterns
difficulty: medium
status: draft
moc: moc-cs
created: 2025-10-15
tags: []
related: [q-java-access-modifiers--programming-languages--medium, q-linkedlist-arraylist-insert-behavior--programming-languages--medium, q-extension-properties--programming-languages--medium]
  - factory-method-pattern
  - builder-pattern
subtopics:
  - creational-patterns
  - object-cloning
---
# Prototype Pattern / Паттерн Прототип

# Question (EN)
> What is the Prototype pattern? When and why should it be used?

# Вопрос (RU)
> Что такое паттерн Прототип? Когда и зачем его следует использовать?

---

## Answer (EN)


### Definition
The Prototype Design Pattern is a creational pattern that enables the creation of new objects by copying an existing object. Prototype allows us to hide the complexity of making new instances from the client. The existing object acts as a prototype and contains the state of the object.

### Problems It Solves
The prototype design pattern solves problems like:
- How can objects be created so that the specific type of object can be determined at runtime?
- How can dynamically loaded classes be instantiated?

Creating objects directly within the class that requires (uses) the objects is inflexible because it commits the class to particular objects at compile-time and makes it impossible to specify which objects to create at run-time.

### Solution
The prototype design pattern describes how to solve such problems:
- Define a `Prototype` object that returns a copy of itself
- Create new objects by copying a `Prototype` object

### When to Use
Use the Prototype Pattern when:
- The classes to instantiate are specified at run-time, for example, by dynamic loading
- To avoid building a class hierarchy of factories that parallels the class hierarchy of products
- When instances of a class can have one of only a few different combinations of state. It may be more convenient to install a corresponding number of prototypes and clone them rather than instantiating the class manually, each time with the appropriate state
- When object creation is expensive compared to cloning
- When the concrete classes to instantiate are unknown until runtime

### Real-World Use Cases
- Spawning new game characters with similar attributes
- Creating consistent UI components in design software
- Cloning data structures for parallel processing

### Implementation Steps
1. Create a prototype interface that declares a cloning method
2. Implement the prototype in concrete classes
3. Use the prototype to clone and produce new objects

### Example in Kotlin

```kotlin
// Prototype interface
interface GameCharacterPrototype {
    fun clone(): GameCharacterPrototype
}

// Concrete class implementing the Prototype
data class GameCharacter(
    val name: String,
    val weapon: String,
    val level: Int
) : GameCharacterPrototype {
    override fun clone(): GameCharacterPrototype {
        return copy()
    }
}

fun main() {
    // Original character
    val originalCharacter = GameCharacter("Knight", "Sword", 5)

    // Cloning the character
    val clonedCharacter = originalCharacter.clone() as GameCharacter

    println("Original Character: $originalCharacter")
    println("Cloned Character: $clonedCharacter")
}
```

**Output:**
```
Original Character: GameCharacter(name=Knight, weapon=Sword, level=5)
Cloned Character: GameCharacter(name=Knight, weapon=Sword, level=5)
```

**Explanation:**
- `GameCharacterPrototype` is the prototype interface that declares a `clone` method
- `GameCharacter` is a concrete class implementing this interface. The data class in Kotlin has a built-in copy method that fits perfectly with the prototype pattern, making cloning easier
- In the main function, an original game character is created. Later, the character is cloned using the `clone` method

### Advantages
- Hides the complexities of instantiating new objects
- Reduces the number of classes
- Allows adding and removing objects at runtime

### Disadvantages
- Requires implementing a cloning mechanism which might be complex
- Deep cloning can be difficult to implement correctly, especially if the classes have complex object graphs with circular references

---



## Ответ (RU)

### Определение
Паттерн проектирования Прототип - это порождающий паттерн, который позволяет создавать новые объекты путем копирования существующего объекта. Прототип позволяет скрыть сложность создания новых экземпляров от клиента. Существующий объект действует как прототип и содержит состояние объекта.

### Решаемые Проблемы
Паттерн прототип решает следующие проблемы:
- Как можно создавать объекты так, чтобы конкретный тип объекта определялся во время выполнения?
- Как можно инстанцировать динамически загружаемые классы?

Создание объектов непосредственно в классе, который требует (использует) эти объекты, негибко, поскольку это привязывает класс к конкретным объектам во время компиляции и делает невозможным указание того, какие объекты создавать во время выполнения.

### Решение
Паттерн прототип описывает, как решить такие проблемы:
- Определить объект `Prototype`, который возвращает копию самого себя
- Создавать новые объекты путем копирования объекта `Prototype`

### Когда Использовать
Используйте паттерн Прототип, когда:
- Классы для инстанцирования указываются во время выполнения, например, при динамической загрузке
- Нужно избежать построения иерархии классов фабрик, которая параллельна иерархии классов продуктов
- Экземпляры класса могут иметь только одну из нескольких различных комбинаций состояний. Может быть удобнее установить соответствующее количество прототипов и клонировать их, чем инстанцировать класс вручную каждый раз с соответствующим состоянием
- Создание объекта дороже по сравнению с клонированием
- Конкретные классы для инстанцирования неизвестны до времени выполнения

### Примеры Использования в Реальном Мире
- Создание новых игровых персонажей с похожими атрибутами
- Создание согласованных UI-компонентов в дизайнерском ПО
- Клонирование структур данных для параллельной обработки

### Шаги Реализации
1. Создать интерфейс прототипа, объявляющий метод клонирования
2. Реализовать прототип в конкретных классах
3. Использовать прототип для клонирования и создания новых объектов

### Пример на Kotlin

```kotlin
// Интерфейс прототипа
interface GameCharacterPrototype {
    fun clone(): GameCharacterPrototype
}

// Конкретный класс, реализующий прототип
data class GameCharacter(
    val name: String,
    val weapon: String,
    val level: Int
) : GameCharacterPrototype {
    override fun clone(): GameCharacterPrototype {
        return copy()
    }
}

fun main() {
    // Оригинальный персонаж
    val originalCharacter = GameCharacter("Knight", "Sword", 5)

    // Клонирование персонажа
    val clonedCharacter = originalCharacter.clone() as GameCharacter

    println("Original Character: $originalCharacter")
    println("Cloned Character: $clonedCharacter")
}
```

**Вывод:**
```
Original Character: GameCharacter(name=Knight, weapon=Sword, level=5)
Cloned Character: GameCharacter(name=Knight, weapon=Sword, level=5)
```

**Объяснение:**
- `GameCharacterPrototype` - это интерфейс прототипа, который объявляет метод `clone`
- `GameCharacter` - конкретный класс, реализующий этот интерфейс. Data-класс в Kotlin имеет встроенный метод copy, который идеально подходит для паттерна прототип, упрощая клонирование
- В функции main создается оригинальный игровой персонаж. Затем персонаж клонируется с помощью метода `clone`

### Преимущества
- Скрывает сложность создания новых объектов
- Уменьшает количество классов
- Позволяет добавлять и удалять объекты во время выполнения

### Недостатки
- Требует реализации механизма клонирования, который может быть сложным
- Глубокое клонирование может быть сложно реализовать правильно, особенно если классы имеют сложные графы объектов с циклическими ссылками

---

## References
- [Prototype Design Pattern - GeeksforGeeks](https://www.geeksforgeeks.org/prototype-design-pattern/)
- [Prototype pattern - Wikipedia](https://en.wikipedia.org/wiki/Prototype_pattern)
- [Prototype Pattern in Java - Java Design Patterns](https://java-design-patterns.com/patterns/prototype/)
- [Prototype Design Pattern in Kotlin](https://www.javaguides.net/2023/10/prototype-design-pattern-in-kotlin.html)
- [Prototype Design Pattern - SourceMaking](https://sourcemaking.com/design_patterns/prototype)
- [Prototype - Refactoring Guru](https://refactoring.guru/design-patterns/prototype)
- [Prototype Software Pattern Kotlin Examples](https://softwarepatterns.com/kotlin/prototype-software-pattern-kotlin-example)

---

**Source:** Kirchhoff-Android-Interview-Questions
**Attribution:** Content adapted from the Kirchhoff repository


---

## Related Questions

### Hub
- [[q-design-patterns-types--design-patterns--medium]] - Design pattern categories overview

### Creational Patterns
- [[q-factory-method-pattern--design-patterns--medium]] - Factory Method pattern
- [[q-abstract-factory-pattern--design-patterns--medium]] - Abstract Factory pattern
- [[q-builder-pattern--design-patterns--medium]] - Builder pattern

### Structural Patterns
- [[q-adapter-pattern--design-patterns--medium]] - Adapter pattern

### Behavioral Patterns
- [[q-strategy-pattern--design-patterns--medium]] - Strategy pattern


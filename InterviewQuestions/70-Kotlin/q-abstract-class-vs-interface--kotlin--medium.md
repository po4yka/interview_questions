---
id: 20251005-235006
title: "Abstract Class vs Interface / Абстрактный класс vs интерфейс"
aliases: []

# Classification
topic: kotlin
subtopics: [abstract-class, interface, oop, inheritance]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository - Kotlin Batch 2

# Workflow & relations
status: draft
moc: moc-kotlin
related: []

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [kotlin, abstract-class, interface, oop, inheritance, difficulty/medium]
---
## Question (EN)
> What is the difference between abstract class and interface in Kotlin?
## Вопрос (RU)
> В чем разница между абстрактным классом и интерфейсом в Kotlin?

---

## Answer (EN)

### Interface

An interface is a blueprint of a class that describes methods a class agrees to implement. **Cannot hold state** (cannot have initialized properties), but can contain default method implementations.

```kotlin
interface Clickable {
    fun click()  // Abstract method
    fun showOff() = println("I'm clickable!")  // Default implementation
}
```

### Abstract Class

An abstract class **can hold state** (can have initialized properties). It's a partially defined class where methods and properties must be implemented by subclasses.

```kotlin
abstract class Animated {
    abstract fun animate()  // Must be implemented

    open fun stopAnimating() {  // Can be overridden
        println("Stopped animating")
    }

    fun animateTwice() {  // Concrete method
        animate()
        animate()
    }
}
```

### Key Differences

| Feature | Abstract Class | Interface |
|---------|----------------|-----------|
| **State** | Can store state (initialized properties) | Cannot store state |
| **Inheritance** | Single inheritance only | Multiple implementation |
| **Constructors** | Has constructors | No constructors |
| **Implementation** | Can provide interface implementation | Cannot provide abstract class implementation |
| **Extends** | Can extend one class + implement interfaces | Can extend multiple interfaces |
| **Access modifiers** | Can use protected, private | Only public members |

### When to Use Abstract Class

- Share code among **closely related classes**
- Classes have **many common methods or fields**
- Need **access modifiers** other than public (protected, private)
- Want to define **non-static, non-final** fields

```kotlin
abstract class Animal(val name: String) {
    protected var age: Int = 0  // State

    abstract fun makeSound()  // Must implement

    fun sleep() {  // Common behavior
        println("$name is sleeping")
    }
}

class Dog(name: String) : Animal(name) {
    override fun makeSound() {
        println("Woof!")
    }
}
```

### When to Use Interface

- **Unrelated classes** would implement it
- Want to specify **behavior** without caring who implements it
- Need **multiple inheritance of type**

```kotlin
interface Comparable<T> {
    fun compareTo(other: T): Int
}

interface Cloneable {
    fun clone(): Any
}

// Any class can implement these
class User : Comparable<User>, Cloneable {
    override fun compareTo(other: User): Int = /* ... */
    override fun clone(): Any = /* ... */
}
```

**English Summary**: Abstract classes can hold state, have constructors, and support single inheritance. Interfaces cannot hold state, have no constructors, and support multiple implementation. Use abstract classes for closely related classes sharing code. Use interfaces for unrelated classes needing to specify behavior or for multiple inheritance.

## Ответ (RU)

### Интерфейс

Интерфейс — это blueprint класса, который описывает методы, которые класс обязуется реализовать. **Не может хранить состояние** (не может иметь инициализированные свойства), но может содержать реализации методов по умолчанию.

```kotlin
interface Clickable {
    fun click()  // Абстрактный метод
    fun showOff() = println("I'm clickable!")  // Реализация по умолчанию
}
```

### Абстрактный класс

Абстрактный класс **может хранить состояние** (может иметь инициализированные свойства). Это частично определенный класс, где методы и свойства должны быть реализованы подклассами.

```kotlin
abstract class Animated {
    abstract fun animate()  // Должен быть реализован

    open fun stopAnimating() {  // Может быть переопределен
        println("Stopped animating")
    }

    fun animateTwice() {  // Конкретный метод
        animate()
        animate()
    }
}
```

### Ключевые отличия

| Функция | Абстрактный класс | Интерфейс |
|---------|-------------------|-----------|
| **Состояние** | Может хранить состояние | Не может хранить состояние |
| **Наследование** | Только одиночное | Множественная реализация |
| **Конструкторы** | Имеет конструкторы | Нет конструкторов |
| **Реализация** | Может предоставить реализацию интерфейса | Не может предоставить реализацию абстрактного класса |
| **Расширяет** | Может расширить один класс + реализовать интерфейсы | Может расширить несколько интерфейсов |

### Когда использовать абстрактный класс

- Делить код между **тесно связанными классами**
- Классы имеют **много общих методов или полей**
- Нужны **модификаторы доступа** кроме public (protected, private)

### Когда использовать интерфейс

- **Несвязанные классы** будут его реализовывать
- Хотите указать **поведение** не заботясь кто реализует
- Нужно **множественное наследование типа**

**Краткое содержание**: Абстрактные классы могут хранить состояние, имеют конструкторы и поддерживают одиночное наследование. Интерфейсы не могут хранить состояние, не имеют конструкторов и поддерживают множественную реализацию. Используйте абстрактные классы для тесно связанных классов, делящих код. Используйте интерфейсы для несвязанных классов или для множественного наследования.

---

## References
- [Interfaces and Abstract Classes - StudyRaid](https://app.studyraid.com/en/read/2427/49034/interfaces-and-abstract-classes)
- [Abstract Methods and Classes - Oracle](https://docs.oracle.com/javase/tutorial/java/IandI/abstract.html)

## Related Questions
- [[q-sealed-classes--kotlin--medium]]

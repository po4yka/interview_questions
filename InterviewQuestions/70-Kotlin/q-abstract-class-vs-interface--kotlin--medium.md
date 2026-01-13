id: kotlin-012
title: Abstract Class vs Interface / Абстрактный класс vs интерфейс
aliases:
- Abstract Class vs Interface
- Абстрактный класс vs интерфейс
topic: kotlin
subtopics:
- classes
- inheritance
- interfaces
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- q-data-class-detailed--kotlin--medium
- q-inheritance-open-final--kotlin--medium
- q-inner-nested-classes--kotlin--medium
created: 2025-10-05
updated: 2025-11-11
tags:
- abstract-classes
- difficulty/medium
- inheritance
- interfaces
- kotlin
- kotlin-features
- oop
sources:
- https://kotlinlang.org/docs/interfaces.html
---
# Вопрос (RU)
> В чём разница между абстрактным классом и интерфейсом в Kotlin?

# Question (EN)
> What's the difference between abstract class and interface in Kotlin?

---

## Ответ (RU)

**Теория Abstract Class vs Interface:**
Абстрактный класс — частично определённый класс, который может хранить состояние (backing fields) и содержать как абстрактные, так и не абстрактные члены. Интерфейс — контракт, который не может иметь собственных backing fields: его свойства либо абстрактные, либо реализованы только через геттеры/сеттеры без поля в самом интерфейсе. В Kotlin интерфейсы поддерживают множественную реализацию, абстрактные классы — только одиночное наследование.

**Основные отличия:**
- **Состояние**: Abstract class может иметь собственные backing fields, interface — нет (backing field появляется в классе-реализации)
- **Наследование**: Abstract class — single inheritance, interface — multiple implementation
- **Конструкторы**: Abstract class может иметь конструктор(ы), interface — нет
- **Реализация**: И абстрактный класс, и интерфейс могут содержать реализации методов (default / concrete methods)
- **Использование**: Abstract class для тесно связанных классов с общей базовой реализацией или состоянием, interface для объявления контрактов поведения, которые могут реализовываться несвязанными классами

**Базовые примеры:**
```kotlin
// ✅ Interface — контракт без собственных backing fields
interface Clickable {
    fun click() // Абстрактный метод
    fun showOff() = println("I'm clickable!") // Реализация по умолчанию
}

// ✅ Abstract class — может хранить состояние
abstract class Animated {
    protected var isRunning = false // ✅ Backing field
    abstract fun animate()
    fun start() { isRunning = true }
}

// ✅ Interface свойства без backing fields в интерфейсе
interface Named {
    val name: String // Абстрактное свойство (accessor абстрактен)
    val displayName: String
        get() = "User: $name" // ✅ Custom getter без backing field в интерфейсе
}
```

**State в interface vs abstract class:**
```kotlin
// ✅ Interface не имеет собственного backing field для этого свойства
interface Counter {
    var count: Int // Accessors абстрактные, реализация и backing field должны быть в классе
}

class MyCounter : Counter {
    override var count: Int = 0 // ✅ Backing field в классе-реализации
}

// ✅ Abstract class может иметь состояние
abstract class Repository {
    private val cache = mutableMapOf<String, Any>() // ✅ Backing field в абстрактном классе

    protected fun getCached(key: String) = cache[key]
    abstract fun fetch(id: String): Any
}
```

**Multiple inheritance:**
```kotlin
// ✅ Interface — множественная реализация
interface Serializable
interface Comparable<T>
interface Cloneable

class Data : Serializable, Comparable<Data>, Cloneable {
    override fun compareTo(other: Data): Int = 0
}

// ❌ Abstract class — только один базовый класс
abstract class BaseViewModel
abstract class BaseRepository
// class MyClass : BaseViewModel(), BaseRepository() // Ошибка!
```

**Access modifiers:**
```kotlin
// ✅ Abstract class — любые модификаторы, как у обычных классов
abstract class Animal {
    protected var age: Int = 0 // ✅ Protected
    private val name: String = "Animal" // ✅ Private
}

// ✅ Interface — члены public по умолчанию, private доступен (Kotlin 1.4+)
// Видимость самого интерфейса по умолчанию public для top-level,
// вложенные интерфейсы наследуют модификатор внешней сущности.
interface Test {
    fun publicMethod() // Public по умолчанию
    private fun privateMethod() {} // ✅ Kotlin 1.4+
}
```

## Дополнительные Вопросы (RU)

- Когда выбирать абстрактный класс вместо интерфейса?
- Чем sealed классы отличаются от абстрактных?
- Эволюция интерфейсов и методы по умолчанию?

## Ссылки (RU)

- https://kotlinlang.org/docs/interfaces.html

## Связанные Вопросы (RU)

### Базовые (Легче)
- [[q-kotlin-enum-classes--kotlin--easy]] - Базовые классы

### Того Же Уровня (Medium)
- [[q-inheritance-open-final--kotlin--medium]] - Наследование
- [[q-inner-nested-classes--kotlin--medium]] - Классы
- [[q-data-class-detailed--kotlin--medium]] - Data классы

### Продвинутые (Сложнее)
- [[q-kotlin-reified-types--kotlin--hard]] - Reified типы

---

## Answer (EN)

**Abstract Class vs Interface Theory:**
Abstract class is a partially defined class that can hold state (backing fields) and contain both abstract and non-abstract members. Interface is a contract that cannot have its own backing fields: its properties are either abstract or implemented via accessors only, without a field in the interface itself. In Kotlin, interfaces support multiple implementation, while abstract classes support only single inheritance for classes.

**Key Differences:**
- **State**: Abstract class can have its own backing fields, interface cannot (the backing field is provided by the implementing class)
- **Inheritance**: Abstract class — single inheritance, interface — multiple implementation
- **Constructors**: Abstract class can have constructors, interface cannot
- **Implementation**: Both abstract class and interface can contain concrete (default) method implementations
- **Usage**: Use abstract class for closely related classes sharing base implementation/state; use interface to define behavior contracts implementable by unrelated classes

**Basic Examples:**
```kotlin
// ✅ Interface — contract without its own backing fields
interface Clickable {
    fun click() // Abstract method
    fun showOff() = println("I'm clickable!") // Default implementation
}

// ✅ Abstract class — can hold state
abstract class Animated {
    protected var isRunning = false // ✅ Backing field
    abstract fun animate()
    fun start() { isRunning = true }
}

// ✅ Interface properties without backing fields in the interface itself
interface Named {
    val name: String // Abstract property (accessor is abstract)
    val displayName: String
        get() = "User: $name" // ✅ Custom getter without backing field in the interface
}
```

**State in Interface vs Abstract Class:**
```kotlin
// ✅ Interface does not get a backing field for this property
interface Counter {
    var count: Int // Accessors are abstract; implementation and backing field must be in the class
}

class MyCounter : Counter {
    override var count: Int = 0 // ✅ Backing field in implementing class
}

// ✅ Abstract class can have state
abstract class Repository {
    private val cache = mutableMapOf<String, Any>() // ✅ Backing field in abstract class

    protected fun getCached(key: String) = cache[key]
    abstract fun fetch(id: String): Any
}
```

**Multiple Inheritance:**
```kotlin
// ✅ Interface — multiple implementation
interface Serializable
interface Comparable<T>
interface Cloneable

class Data : Serializable, Comparable<Data>, Cloneable {
    override fun compareTo(other: Data): Int = 0
}

// ❌ Abstract class — only one superclass allowed
abstract class BaseViewModel
abstract class BaseRepository
// class MyClass : BaseViewModel(), BaseRepository() // Error!
```

**Access Modifiers:**
```kotlin
// ✅ Abstract class — same possibilities as regular classes
abstract class Animal {
    protected var age: Int = 0 // ✅ Protected
    private val name: String = "Animal" // ✅ Private
}

// ✅ Interface — members are public by default; private is available (Kotlin 1.4+)
// Top-level interfaces are public by default; nested interfaces follow their containing declaration.
interface Test {
    fun publicMethod() // Public by default
    private fun privateMethod() {} // ✅ Kotlin 1.4+
}
```

## Follow-ups

- When to choose abstract class over interface?
- How do sealed classes differ from abstract classes?
- Interface evolution and default methods?

## References

- https://kotlinlang.org/docs/interfaces.html

## Related Questions

### Prerequisites (Easier)
- [[q-kotlin-enum-classes--kotlin--easy]] - Basic classes

### Related (Medium)
- [[q-inheritance-open-final--kotlin--medium]] - Inheritance
- [[q-inner-nested-classes--kotlin--medium]] - Classes
- [[q-data-class-detailed--kotlin--medium]] - Data classes

### Advanced (Harder)
- [[q-kotlin-reified-types--kotlin--hard]] - Reified types

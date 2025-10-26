---
id: 20251005-235006
title: "Abstract Class vs Interface / Абстрактный класс vs интерфейс"
aliases: ["Abstract Class vs Interface", "Абстрактный класс vs интерфейс"]
topic: kotlin
subtopics: [classes, inheritance, interfaces]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-inheritance-open-final--kotlin--medium, q-inner-nested-classes--kotlin--medium, q-data-class-detailed--kotlin--medium]
created: 2025-10-05
updated: 2025-01-25
tags: [kotlin, abstract-class, interface, inheritance, oop, kotlin-features, difficulty/medium]
sources: [https://kotlinlang.org/docs/interfaces.html]
---

# Вопрос (RU)
> В чём разница между абстрактным классом и интерфейсом в Kotlin?

# Question (EN)
> What's the difference between abstract class and interface in Kotlin?

---

## Ответ (RU)

**Теория Abstract Class vs Interface:**
Абстрактный класс - частично определённый класс с возможностью хранить состояние (backing fields). Интерфейс - контракт без состояния, может иметь только custom getters без backing fields. В Kotlin интерфейсы поддерживают множественную реализацию, абстрактные классы - только одиночное наследование.

**Основные отличия:**
- **Состояние**: Abstract class может иметь backing fields, interface - нет
- **Наследование**: Abstract class - single inheritance, interface - multiple implementation
- **Конструкторы**: Abstract class может иметь, interface - нет
- **Использование**: Abstract class для тесно связанных классов, interface для контрактов

**Базовые примеры:**
```kotlin
// ✅ Interface - контракт без состояния
interface Clickable {
    fun click() // Абстрактный метод
    fun showOff() = println("I'm clickable!") // Реализация по умолчанию
}

// ✅ Abstract class - может хранить состояние
abstract class Animated {
    protected var isRunning = false // ✅ Backing field
    abstract fun animate()
    fun start() { isRunning = true }
}

// ✅ Interface properties без backing fields
interface Named {
    val name: String // Абстрактное свойство
    val displayName: String
        get() = "User: $name" // ✅ Custom getter без backing field
}
```

**State в interface vs abstract class:**
```kotlin
// ❌ Interface не может иметь backing fields
interface Counter {
    var count: Int // Должно быть переопределено
}

class MyCounter : Counter {
    override var count: Int = 0 // ✅ Backing field в классе
}

// ✅ Abstract class может иметь состояние
abstract class Repository {
    private val cache = mutableMapOf<String, Any>() // ✅ Backing field

    protected fun getCached(key: String) = cache[key]
    abstract fun fetch(id: String): Any
}
```

**Multiple inheritance:**
```kotlin
// ✅ Interface - множественная реализация
interface Serializable
interface Comparable<T>
interface Cloneable

class Data : Serializable, Comparable<Data>, Cloneable {
    override fun compareTo(other: Data): Int = 0
}

// ❌ Abstract class - только один
abstract class BaseViewModel
abstract class BaseRepository
// class MyClass : BaseViewModel(), BaseRepository() // Ошибка!
```

**Access modifiers:**
```kotlin
// ✅ Abstract class - любые модификаторы
abstract class Animal {
    protected var age: Int = 0 // ✅ Protected
    private val name: String = "Animal" // ✅ Private
}

// ✅ Interface - public по умолчанию, private доступен (Kotlin 1.4+)
interface Test {
    fun publicMethod() // Public
    private fun privateMethod() {} // ✅ Kotlin 1.4+
}
```

---

## Answer (EN)

**Abstract Class vs Interface Theory:**
Abstract class is partially defined class that can hold state (backing fields). Interface is contract without state, can only have custom getters without backing fields. In Kotlin, interfaces support multiple implementation, abstract classes support only single inheritance.

**Key Differences:**
- **State**: Abstract class can have backing fields, interface cannot
- **Inheritance**: Abstract class - single inheritance, interface - multiple implementation
- **Constructors**: Abstract class can have, interface cannot
- **Usage**: Abstract class for closely related classes, interface for contracts

**Basic Examples:**
```kotlin
// ✅ Interface - contract without state
interface Clickable {
    fun click() // Abstract method
    fun showOff() = println("I'm clickable!") // Default implementation
}

// ✅ Abstract class - can hold state
abstract class Animated {
    protected var isRunning = false // ✅ Backing field
    abstract fun animate()
    fun start() { isRunning = true }
}

// ✅ Interface properties without backing fields
interface Named {
    val name: String // Abstract property
    val displayName: String
        get() = "User: $name" // ✅ Custom getter without backing field
}
```

**State in Interface vs Abstract Class:**
```kotlin
// ❌ Interface cannot have backing fields
interface Counter {
    var count: Int // Must be overridden
}

class MyCounter : Counter {
    override var count: Int = 0 // ✅ Backing field in class
}

// ✅ Abstract class can have state
abstract class Repository {
    private val cache = mutableMapOf<String, Any>() // ✅ Backing field

    protected fun getCached(key: String) = cache[key]
    abstract fun fetch(id: String): Any
}
```

**Multiple Inheritance:**
```kotlin
// ✅ Interface - multiple implementation
interface Serializable
interface Comparable<T>
interface Cloneable

class Data : Serializable, Comparable<Data>, Cloneable {
    override fun compareTo(other: Data): Int = 0
}

// ❌ Abstract class - only one
abstract class BaseViewModel
abstract class BaseRepository
// class MyClass : BaseViewModel(), BaseRepository() // Error!
```

**Access Modifiers:**
```kotlin
// ✅ Abstract class - any modifiers
abstract class Animal {
    protected var age: Int = 0 // ✅ Protected
    private val name: String = "Animal" // ✅ Private
}

// ✅ Interface - public by default, private available (Kotlin 1.4+)
interface Test {
    fun publicMethod() // Public
    private fun privateMethod() {} // ✅ Kotlin 1.4+
}
```

## Follow-ups

- When to choose abstract class over interface?
- How do sealed classes differ from abstract classes?
- Interface evolution and default methods?

## References

- [[c-oop-fundamentals]]
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

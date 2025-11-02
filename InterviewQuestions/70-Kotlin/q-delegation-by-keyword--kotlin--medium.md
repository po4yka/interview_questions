---
id: kotlin-237
title: "Class Delegation with 'by' Keyword / Делегирование класса с ключевым словом 'by'"
aliases: ["Class Delegation", "Делегирование класса"]
topic: kotlin
subtopics: [classes, delegation, kotlin-features]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-data-class-detailed--kotlin--medium, q-inheritance-open-final--kotlin--medium, q-kotlin-lateinit--kotlin--medium]
created: "2025-10-12"
updated: 2025-01-25
tags: [by-keyword, classes, delegation, difficulty/medium, kotlin, kotlin-features]
sources: [https://kotlinlang.org/docs/delegation.html]
date created: Sunday, October 12th 2025, 1:58:08 pm
date modified: Saturday, November 1st 2025, 5:43:26 pm
---

# Вопрос (RU)
> Что такое делегирование класса с ключевым словом 'by' в Kotlin?

# Question (EN)
> What is class delegation with the 'by' keyword in Kotlin?

---

## Ответ (RU)

**Теория делегирования:**
Ключевое слово `by` в Kotlin используется для реализации паттерна делегирования. Вместо наследования класс может реализовать интерфейс путём делегирования всех его публичных членов указанному объекту. Это позволяет использовать композицию вместо наследования и избежать проблем множественного наследования.

**Основные концепции:**
- **Делегирование интерфейса**: Реализация интерфейса через делегирование всех его методов другому объекту
- **Использование 'by'**: Автоматическая генерация делегированных методов
- **Сокращение boilerplate**: Код для делегирования генерируется компилятором автоматически

**Базовое делегирование:**
```kotlin
interface Printer {
    fun print(message: String)
}

class ConsolePrinter : Printer {
    override fun print(message: String) {
        println(message)
    }
}

// ✅ Использование делегирования
class Logger(private val printer: Printer) : Printer by printer {
    fun log(message: String) {
        printer.print("[LOG] $message")
    }
}

// Usage: не нужно переопределять методы Printer
val logger = Logger(ConsolePrinter())
logger.print("Hello") // Делегируется в printer
logger.log("Info") // Логирование через метод logger
```

**Делегирование нескольких интерфейсов:**
```kotlin
interface A { fun a() }
interface B { fun b() }

class AImpl : A {
    override fun a() = println("A")
}

class BImpl : B {
    override fun b() = println("B")
}

// ✅ Делегирование нескольких интерфейсов
class Composite(a: A, b: B) : A by a, B by b

fun main() {
    val composite = Composite(AImpl(), BImpl())
    composite.a() // Делегируется в a
    composite.b() // Делегируется в b
}
```

**Переопределение делегированных методов:**
```kotlin
interface Repository {
    fun findById(id: String): String
}

class DbRepository : Repository {
    override fun findById(id: String): String = "DB result"
}

// ✅ Частичное переопределение
class CachedRepository(private val dbRepo: Repository) : Repository by dbRepo {
    private val cache = mutableMapOf<String, String>()

    override fun findById(id: String): String {
        return cache.getOrPut(id) {
            dbRepo.findById(id) // Вызываем оригинальный метод
        }
    }
}
```

**Делегирование и наследование:**
```kotlin
open class Base(val name: String) {
    open fun describe() = "Base: $name"
}

interface Greetable {
    fun greet(): String
}

class GreetingImpl : Greetable {
    override fun greet() = "Hello!"
}

// ✅ Комбинация наследования и делегирования
class Derived(name: String, greeter: Greetable) :
    Base(name), Greetable by greeter {

    override fun describe() = super.describe() + " + " + greet()
}

fun main() {
    val derived = Derived("Test", GreetingImpl())
    println(derived.describe()) // Base: Test + Hello!
}
```

**Классическое использование - отказ от интерфейса:**
```kotlin
interface ReadOnlyCollection {
    fun size(): Int
    fun isEmpty(): Boolean
}

class MutableCollection(private val items: MutableList<String>) : ReadOnlyCollection {
    override fun size() = items.size
    override fun isEmpty() = items.isEmpty()
    fun add(item: String) = items.add(item)
}

// ✅ Делегирование упрощает код
class ReadOnlyWrapper(private val collection: MutableCollection) :
    ReadOnlyCollection by collection {
    // Только методы ReadOnlyCollection доступны
}
```

---

## Answer (EN)

**Delegation Theory:**
The `by` keyword in Kotlin implements the delegation pattern. Instead of inheritance, a class can implement an interface by delegating all its public members to a specified object. This enables composition over inheritance and avoids multiple inheritance problems.

**Core Concepts:**
- **Interface Delegation**: Implementing interface by delegating all its methods to another object
- **Using 'by'**: Automatic generation of delegated methods
- **Boilerplate Reduction**: Delegation code is generated automatically by compiler

**Basic Delegation:**
```kotlin
interface Printer {
    fun print(message: String)
}

class ConsolePrinter : Printer {
    override fun print(message: String) {
        println(message)
    }
}

// ✅ Using delegation
class Logger(private val printer: Printer) : Printer by printer {
    fun log(message: String) {
        printer.print("[LOG] $message")
    }
}

// Usage: no need to override Printer methods
val logger = Logger(ConsolePrinter())
logger.print("Hello") // Delegated to printer
logger.log("Info") // Logging through logger method
```

**Multiple Interface Delegation:**
```kotlin
interface A { fun a() }
interface B { fun b() }

class AImpl : A {
    override fun a() = println("A")
}

class BImpl : B {
    override fun b() = println("B")
}

// ✅ Delegating multiple interfaces
class Composite(a: A, b: B) : A by a, B by b

fun main() {
    val composite = Composite(AImpl(), BImpl())
    composite.a() // Delegated to a
    composite.b() // Delegated to b
}
```

**Overriding Delegated Methods:**
```kotlin
interface Repository {
    fun findById(id: String): String
}

class DbRepository : Repository {
    override fun findById(id: String): String = "DB result"
}

// ✅ Partial override
class CachedRepository(private val dbRepo: Repository) : Repository by dbRepo {
    private val cache = mutableMapOf<String, String>()

    override fun findById(id: String): String {
        return cache.getOrPut(id) {
            dbRepo.findById(id) // Call original method
        }
    }
}
```

**Delegation and Inheritance:**
```kotlin
open class Base(val name: String) {
    open fun describe() = "Base: $name"
}

interface Greetable {
    fun greet(): String
}

class GreetingImpl : Greetable {
    override fun greet() = "Hello!"
}

// ✅ Combining inheritance and delegation
class Derived(name: String, greeter: Greetable) :
    Base(name), Greetable by greeter {

    override fun describe() = super.describe() + " + " + greet()
}

fun main() {
    val derived = Derived("Test", GreetingImpl())
    println(derived.describe()) // Base: Test + Hello!
}
```

**Classic Use Case - Interface Segregation:**
```kotlin
interface ReadOnlyCollection {
    fun size(): Int
    fun isEmpty(): Boolean
}

class MutableCollection(private val items: MutableList<String>) : ReadOnlyCollection {
    override fun size() = items.size
    override fun isEmpty() = items.isEmpty()
    fun add(item: String) = items.add(item)
}

// ✅ Delegation simplifies code
class ReadOnlyWrapper(private val collection: MutableCollection) :
    ReadOnlyCollection by collection {
    // Only ReadOnlyCollection methods accessible
}
```

## Follow-ups

- When to use delegation vs inheritance?
- How does delegation help with composition over inheritance?
- Performance implications of delegation?

## References

- https://kotlinlang.org/docs/delegation.html

## Related Questions

### Prerequisites (Easier)
- [[q-inheritance-open-final--kotlin--medium]] - Inheritance basics

### Related (Medium)
- [[q-data-class-detailed--kotlin--medium]] - Data classes
- [[q-class-initialization-order--kotlin--medium]] - Class initialization

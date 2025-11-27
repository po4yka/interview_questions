---
id: kotlin-237
title: "Class Delegation with 'by' Keyword / Делегирование класса с ключевым словом 'by'"
aliases: ["Class Delegation", "Делегирование класса"]
topic: kotlin
subtopics: [delegation, kotlin-features]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-data-class-detailed--kotlin--medium, q-inheritance-open-final--kotlin--medium, q-kotlin-lateinit--kotlin--medium]
created: 2025-10-12
updated: 2025-11-09
tags: [by-keyword, classes, delegation, difficulty/medium, kotlin, kotlin-features]
sources: ["https://kotlinlang.org/docs/delegation.html"]
date created: Sunday, October 12th 2025, 1:58:08 pm
date modified: Tuesday, November 25th 2025, 8:53:52 pm
---
# Вопрос (RU)
> Что такое делегирование класса с ключевым словом `by` в Kotlin?

# Question (EN)
> What is class delegation with the `by` keyword in Kotlin?

---

## Ответ (RU)

**Теория делегирования:**
Ключевое слово `by` в Kotlin используется для реализации паттерна делегирования. Вместо наследования класс может объявить реализацию интерфейса, делегируя реализацию всех его членов указанному объекту-делегату. Компилятор генерирует за вас методы, которые просто перенаправляют вызовы делегату. Это позволяет использовать композицию вместо наследования и избежать проблем множественного наследования. Делегирование через `by` для классов в Kotlin возможно только для интерфейсов, а не для конкретных (неинтерфейсных) базовых классов.

**Основные концепции:**
- **Делегирование интерфейса**: Реализация интерфейса через делегирование всех его методов (и свойств интерфейса) другому объекту
- **Использование `by`**: Автоматическая генерация делегированных методов компилятором, которые перенаправляют вызовы объекту-делегату
- **Сокращение boilerplate**: Код для делегирования генерируется компилятором автоматически
- Класс может переопределить любые делегированные методы при необходимости (они имеют приоритет над сгенерированными).
- См. также: [[c-kotlin]]

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

// Использование делегирования
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

// Делегирование нескольких интерфейсов
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

// Частичное переопределение
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

// Комбинация наследования и делегирования интерфейса
class Derived(name: String, greeter: Greetable) :
    Base(name), Greetable by greeter {

    override fun describe() = super.describe() + " + " + greet()
}

fun main() {
    val derived = Derived("Test", GreetingImpl())
    println(derived.describe()) // Base: Test + Hello!
}
```

**Использование для ограничения API (read-only обёртка):**
```kotlin
// Пример с пользовательскими типами, не связанными со стандартными коллекциями Kotlin
interface ReadOnlyCollection {
    fun size(): Int
    fun isEmpty(): Boolean
}

class MutableCollection(private val items: MutableList<String>) : ReadOnlyCollection {
    override fun size() = items.size
    override fun isEmpty() = items.isEmpty()
    fun add(item: String) = items.add(item)
}

// Делегирование упрощает код и ограничивает внешний контракт
class ReadOnlyWrapper(private val collection: MutableCollection) :
    ReadOnlyCollection by collection {
    // Снаружи доступны только методы ReadOnlyCollection
}
```

## Дополнительные Вопросы (RU)

- Когда использовать делегирование вместо наследования?
- Как делегирование помогает реализовать композицию вместо наследования?
- Каковы накладные расходы и влияние делегирования на производительность?

## Ссылки (RU)

- https://kotlinlang.org/docs/delegation.html

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-inheritance-open-final--kotlin--medium]] - Основы наследования

### Связанные (средний уровень)
- [[q-data-class-detailed--kotlin--medium]] - Data классы
- [[q-class-initialization-order--kotlin--medium]] - Порядок инициализации классов

---

## Answer (EN)

**Delegation Theory:**
The `by` keyword in Kotlin implements the delegation pattern. Instead of inheritance, a class can declare that it implements an interface by delegating the implementation of all its members to a specified delegate object. The compiler generates the forwarding members for you, which simply call the corresponding members on the delegate. This enables composition over inheritance and avoids multiple inheritance problems. Class delegation with `by` in Kotlin applies to interfaces only (you cannot delegate to a concrete superclass type using `by`).

**Core Concepts:**
- **Interface Delegation**: Implementing an interface by delegating all its methods (and properties declared in the interface) to another object
- **Using `by`**: Automatic generation of delegated methods by the compiler that forward calls to the delegate object
- **Boilerplate Reduction**: Delegation code is generated automatically by the compiler
- The delegating class can override any delegated members if needed (its own implementations take precedence over generated ones).
- See also: [[c-kotlin]]

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

// Using delegation
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

// Delegating multiple interfaces
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

// Partial override
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

// Combining inheritance and interface delegation
class Derived(name: String, greeter: Greetable) :
    Base(name), Greetable by greeter {

    override fun describe() = super.describe() + " + " + greet()
}

fun main() {
    val derived = Derived("Test", GreetingImpl())
    println(derived.describe()) // Base: Test + Hello!
}
```

**Use Case - Restricting Public API via Read-Only Wrapper:**
```kotlin
// Example with custom types, not related to Kotlin standard collection types
interface ReadOnlyCollection {
    fun size(): Int
    fun isEmpty(): Boolean
}

class MutableCollection(private val items: MutableList<String>) : ReadOnlyCollection {
    override fun size() = items.size
    override fun isEmpty() = items.isEmpty()
    fun add(item: String) = items.add(item)
}

// Delegation simplifies code and restricts the exposed contract
class ReadOnlyWrapper(private val collection: MutableCollection) :
    ReadOnlyCollection by collection {
    // From the outside, only ReadOnlyCollection methods are accessible
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

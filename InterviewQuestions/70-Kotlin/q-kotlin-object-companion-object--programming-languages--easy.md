---
id: lang-088
title: "Kotlin Object Companion Object / Object и Companion Object в Kotlin"
aliases: [Kotlin Object Companion Object, Object и Companion Object v Kotlin]
topic: kotlin
subtopics: [c-kotlin, c-kotlin-features]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-kotlin-features, q-data-class-detailed--kotlin--medium, q-kotlin-flow-basics--kotlin--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [companion-object, difficulty/easy, object, singleton]
date created: Friday, October 31st 2025, 6:30:57 pm
date modified: Tuesday, November 25th 2025, 8:53:50 pm
---

# Вопрос (RU)
> Что такое object / companion object?

# Question (EN)
> What is object / companion object?

## Ответ (RU)

**object** и **companion object** используются для реализации различных паттернов и функциональностей, включая паттерн одиночка (singleton), объявление "статических" членов и функций, а также для создания объектов без необходимости явного вызова конструктора.

**1. object** — декларация одиночного экземпляра (object declaration)

Используется для объявления **единственного экземпляра** (singleton) с ленивой инициализацией при первом обращении.

```kotlin
object DatabaseManager {
    val connection = "Connection string"

    fun connect() {
        println("Connecting to database...")
    }
}

// Использование — без создания экземпляра
DatabaseManager.connect()
println(DatabaseManager.connection)
```

Отдельно есть **object expression** (анонимные объекты), создающие новый объект при каждом использовании, и они не являются синглтоном:

```kotlin
val listener = object : Any() {
    fun onEvent() = println("Event")
}
```

**2. companion object** — "статические" члены класса

Объявляется внутри класса и используется для объявления членов, доступных **через имя класса без создания экземпляра**. Это не настоящие `static`, но часто используется аналогично.

```kotlin
class User(val name: String) {
    companion object {
        const val MAX_AGE = 120

        fun create(name: String): User {
            return User(name)
        }
    }
}

// Использование — доступ без экземпляра
val maxAge = User.MAX_AGE
val user = User.create("Alice")
```

`companion object` сам по себе является объектом (одиночным экземпляром), ассоциированным с классом; к нему можно обращаться как `User.Companion`, либо напрямую через `User.create()` / `User.MAX_AGE`.

### Сравнение

| Характеристика        | object (декларация)              | companion object                     |
|-----------------------|----------------------------------|--------------------------------------|
| Расположение          | Верхний уровень / внутри скоупа | Внутри класса                        |
| Назначение            | Отдельный синглтон-объект       | Статик-подобные члены для класса    |
| Доступ                | ObjectName.member               | ClassName.member или ClassName.Companion.member |
| Экземпляр             | Один экземпляр на декларацию    | Один экземпляр на каждый класс      |

### Примеры Использования Object

**Синглтон для конфигурации:**
```kotlin
object AppConfig {
    var apiKey: String = ""
    var baseUrl: String = "https://api.example.com"
}

// Один разделяемый экземпляр
AppConfig.apiKey = "12345"
```

**Анонимный объект в качестве слушателя:**
```kotlin
val clickListener = object : View.OnClickListener {
    override fun onClick(v: View?) {
        println("Clicked!")
    }
}
```

**Реализация интерфейса анонимным объектом:**
```kotlin
interface Printer {
    fun print()
}

val printer = object : Printer {
    override fun print() {
        println("Printing...")
    }
}
```

### Примеры Использования Companion Object

**Фабричные методы:**
```kotlin
class Person private constructor(val name: String, val age: Int) {
    companion object {
        fun newborn(name: String) = Person(name, 0)
        fun adult(name: String) = Person(name, 18)
    }
}

val baby = Person.newborn("Alice")
val adult = Person.adult("Bob")
```

**Константы:**
```kotlin
class Circle(val radius: Double) {
    companion object {
        const val PI = 3.14159

        fun area(radius: Double) = PI * radius * radius
    }
}

val area = Circle.area(5.0)
```

**Именованный companion object:**
```kotlin
class MyClass {
    companion object Factory {
        fun create(): MyClass = MyClass()
    }
}

val obj1 = MyClass.create()
val obj2 = MyClass.Factory.create()
```

**companion object реализует интерфейс:**
```kotlin
interface JsonSerializer {
    fun toJson(): String
}

class UserWithSerializer(val name: String) {
    companion object : JsonSerializer {
        override fun toJson(): String {
            return """{"type": "User"}"""
        }
    }
}

val json = UserWithSerializer.toJson()
```

### Ключевые Отличия

```kotlin
// object declaration — отдельный синглтон
object Logger {
    fun log(msg: String) = println(msg)
}
Logger.log("Message")  // Прямой доступ по имени объекта

// companion object — привязан к классу
class Database {
    companion object {
        fun connect() = println("Connected")
    }
}
Database.connect()  // Доступ через имя класса
```

- `object` (декларация): отдельный синглтон-объект, доступный по своему имени.
- `companion object`: синглтон-объект, привязанный к классу; его члены доступны через имя класса.
- `object expressions` (анонимные объекты): создают новый экземпляр при каждом использовании и не являются синглтоном.

---

## Answer (EN)

**object** and **companion object** are used to implement various patterns and functionalities, including the singleton pattern, declaring static-like members/functions, and creating objects without explicit constructor calls.

**1. object** - Object Declaration (Singleton Pattern)

Used to create a **single instance** (object declaration) with lazy initialization on first access.

```kotlin
object DatabaseManager {
    val connection = "Connection string"

    fun connect() {
        println("Connecting to database...")
    }
}

// Usage - no need to instantiate
DatabaseManager.connect()
println(DatabaseManager.connection)
```

Note: Kotlin also has **object expressions** (anonymous objects) which create a new instance each time and are NOT singletons:

```kotlin
val listener = object : Any() {
    fun onEvent() = println("Event")
}
```

**2. companion object** - Static-like Members

Declared inside a class to provide members accessible **without creating an instance**. It is not a Java-style `static`, but it's often used similarly.

```kotlin
class User(val name: String) {
    companion object {
        const val MAX_AGE = 120

        fun create(name: String): User {
            return User(name)
        }
    }
}

// Usage - access without instance
val maxAge = User.MAX_AGE
val user = User.create("Alice")
```

A `companion object` itself is a single object associated with the class; it can be referenced as `User.Companion` or via the class name directly (e.g., `User.create()`).

**Comparison:**

| Feature | object (declaration) | companion object |
|---------|----------------------|------------------|
| **Location** | Top-level / inside another scope | Inside a class |
| **Purpose** | Standalone singleton object | Static-like members for the class |
| **Access** | ObjectName.member | ClassName.member or ClassName.Companion.member |
| **Instance** | Single instance (declaration) | Single instance per enclosing class |

**object Uses:**

**Singleton:**
```kotlin
object AppConfig {
    var apiKey: String = ""
    var baseUrl: String = "https://api.example.com"
}

// Single shared instance
AppConfig.apiKey = "12345"
```

**Anonymous Objects (Object Expressions):**
```kotlin
val clickListener = object : View.OnClickListener {
    override fun onClick(v: View?) {
        println("Clicked!")
    }
}
```

**Object Expression with Interface:**
```kotlin
interface Printer {
    fun print()
}

val printer = object : Printer {
    override fun print() {
        println("Printing...")
    }
}
```

**companion object Uses:**

**Factory Methods:**
```kotlin
class Person private constructor(val name: String, val age: Int) {
    companion object {
        fun newborn(name: String) = Person(name, 0)
        fun adult(name: String) = Person(name, 18)
    }
}

val baby = Person.newborn("Alice")
val adult = Person.adult("Bob")
```

**Constants:**
```kotlin
class Circle(val radius: Double) {
    companion object {
        const val PI = 3.14159

        fun area(radius: Double) = PI * radius * radius
    }
}

val area = Circle.area(5.0)
```

**Named companion object:**
```kotlin
class MyClass {
    companion object Factory {
        fun create(): MyClass = MyClass()
    }
}

// Both work
val obj1 = MyClass.create()
val obj2 = MyClass.Factory.create()
```

**Implementing Interfaces with companion object:**
```kotlin
interface JsonSerializer {
    fun toJson(): String
}

class UserWithSerializer(val name: String) {
    companion object : JsonSerializer {
        override fun toJson(): String {
            return """{"type": "User"}"""
        }
    }
}

val json = UserWithSerializer.toJson()
```

**Key Differences:**

```kotlin
// object declaration - standalone singleton
object Logger {
    fun log(msg: String) = println(msg)
}
Logger.log("Message")  // Direct access

// companion object - attached to class
class Database {
    companion object {
        fun connect() = println("Connected")
    }
}
Database.connect()  // Access via class name
```

**Summary:**

- **object (declaration):** creates a singleton object (one instance per declaration, lazily initialized) accessible by its name.
- **companion object:** a singleton object attached to a class; its members are accessible via the class name.
- **object expressions (anonymous objects):** create new instances and are not singletons.
- Both `object` declarations and `companion object` remove the need for explicit instantiation in common use cases.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия от Java (например, отсутствие настоящего `static`, использование companion object, аннотация `@JvmStatic`)?
- Когда вы бы использовали это на практике?
- Какие распространенные ошибки стоит избегать?

## Follow-ups

- What are the key differences between this and Java (e.g., lack of true `static`, use of companion objects, `@JvmStatic`)?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Related Questions

- [[q-kotlin-fold-reduce--kotlin--medium]]
- [[q-data-class-detailed--kotlin--medium]]
- [[q-kotlin-flow-basics--kotlin--medium]]

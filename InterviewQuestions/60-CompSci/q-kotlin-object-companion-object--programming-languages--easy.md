---
tags:
  - companion-object
  - kotlin
  - object
  - programming-languages
  - singleton
  - static-members
difficulty: easy
---

# Что такое object / companion object?

**English**: What is object / companion object?

## Answer

**object** and **companion object** are used to implement various patterns and functionalities, including singleton pattern, declaring static members/functions, and creating objects without explicit instantiation.

**1. object** - Singleton Pattern

Used to create a **single instance** of a class (singleton pattern).

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

**2. companion object** - Static Members

Used inside a class to declare members accessible **without creating an instance** (similar to static members).

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

**Comparison:**

| Feature | object | companion object |
|---------|--------|------------------|
| **Location** | Standalone | Inside class |
| **Purpose** | Singleton | Static-like members |
| **Access** | ObjectName.member | ClassName.member |
| **Instance** | Single instance | Part of enclosing class |

**object Uses:**

**Singleton:**
```kotlin
object AppConfig {
    var apiKey: String = ""
    var baseUrl: String = "https://api.example.com"
}

// Single instance across app
AppConfig.apiKey = "12345"
```

**Anonymous Objects:**
```kotlin
val clickListener = object : View.OnClickListener {
    override fun onClick(v: View?) {
        println("Clicked!")
    }
}
```

**Object Expression:**
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

**Implementing Interfaces:**
```kotlin
interface JsonSerializer {
    fun toJson(): String
}

class User(val name: String) {
    companion object : JsonSerializer {
        override fun toJson(): String {
            return """{"type": "User"}"""
        }
    }
}

val json = User.toJson()
```

**Key Differences:**

```kotlin
// object - standalone singleton
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

- **object**: Creates **singleton** - single instance for entire application
- **companion object**: Declares **static-like members** accessible via class name
- **object**: Standalone declaration
- **companion object**: Inside class declaration
- Both eliminate need for explicit instantiation

## Ответ

**object** и **companion object** используются для реализации различных паттернов и функциональностей, включая паттерн одиночка (singleton), объявление статических членов и функций, а также для реализации объектов без необходимости явного создания экземпляра класса.

**object** используется для создания одиночного экземпляра класса (реализации паттерна singleton).

**companion object** используется внутри класса и служит для объявления членов класса, доступных без создания экземпляра этого класса (аналогично статическим членам).


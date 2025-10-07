---
tags:
  - programming-languages
difficulty: hard
status: draft
---

# What is object / companion object?

**English**: What is object / companion object in Kotlin?

## Answer

`object` and `companion object` are used to implement various patterns and functionalities in Kotlin:

**object declaration:**
- Used to create a single instance of a class (Singleton pattern)
- Thread-safe by default
- Lazily initialized when first accessed
- Cannot have constructors (automatically instantiated)
- Can inherit from classes and implement interfaces

**companion object:**
- Declared inside a class
- Used to declare members accessible without creating an instance of the class
- Similar to static members in Java
- Can implement interfaces
- Can have extension functions
- Only one companion object per class
- Can be named (optional)

### Code Examples

**Object declaration (Singleton):**
```kotlin
// Simple singleton
object DatabaseConnection {
    private var isConnected = false

    fun connect() {
        if (!isConnected) {
            println("Connecting to database...")
            isConnected = true
        }
    }

    fun disconnect() {
        if (isConnected) {
            println("Disconnecting from database...")
            isConnected = false
        }
    }
}

// Usage
fun main() {
    DatabaseConnection.connect()     // Connecting to database...
    DatabaseConnection.disconnect()  // Disconnecting from database...
}
```

**Object with inheritance and interfaces:**
```kotlin
interface ClickListener {
    fun onClick()
}

open class BaseLogger {
    open fun log(message: String) {
        println("Log: $message")
    }
}

object Logger : BaseLogger(), ClickListener {
    override fun log(message: String) {
        println("[${System.currentTimeMillis()}] $message")
    }

    override fun onClick() {
        log("Button clicked")
    }
}

fun main() {
    Logger.log("Application started")
    Logger.onClick()
}
```

**Companion object (static-like members):**
```kotlin
class User(val id: Int, val name: String) {
    companion object {
        private var nextId = 1

        // Factory method
        fun create(name: String): User {
            return User(nextId++, name)
        }

        // Constants
        const val MIN_NAME_LENGTH = 3
        const val MAX_NAME_LENGTH = 50
    }

    init {
        require(name.length >= MIN_NAME_LENGTH) {
            "Name too short"
        }
    }
}

// Usage
fun main() {
    val user1 = User.create("Alice")
    val user2 = User.create("Bob")

    println("${user1.name} has ID ${user1.id}")  // Alice has ID 1
    println("${user2.name} has ID ${user2.id}")  // Bob has ID 2

    println("Min name length: ${User.MIN_NAME_LENGTH}")
}
```

**Named companion object:**
```kotlin
class MyClass {
    companion object Factory {
        fun create(): MyClass = MyClass()
    }
}

// Can be called with or without name
fun main() {
    val obj1 = MyClass.create()           // Using companion object
    val obj2 = MyClass.Factory.create()   // Using companion object name
}
```

**Companion object with interface:**
```kotlin
interface JsonSerializer {
    fun toJson(): String
}

class Person(val name: String, val age: Int) {
    companion object : JsonSerializer {
        override fun toJson(): String {
            return """{"type": "Person"}"""
        }

        fun fromJson(json: String): Person {
            // Parse JSON and create Person
            return Person("Unknown", 0)
        }
    }

    fun toJson(): String {
        return """{"name": "$name", "age": $age}"""
    }
}

fun main() {
    val person = Person("Alice", 30)
    println(person.toJson())              // Instance method
    println(Person.toJson())               // Companion object method
    val newPerson = Person.fromJson("{}")  // Factory method
}
```

**Anonymous object (object expression):**
```kotlin
interface OnClickListener {
    fun onClick()
    fun onLongClick()
}

fun setClickListener(listener: OnClickListener) {
    listener.onClick()
}

fun main() {
    // Anonymous object (like anonymous inner class in Java)
    setClickListener(object : OnClickListener {
        override fun onClick() {
            println("Clicked!")
        }

        override fun onLongClick() {
            println("Long clicked!")
        }
    })
}
```

**Companion object extension:**
```kotlin
class Person(val name: String) {
    companion object {
        // Companion object members
    }
}

// Extension function for companion object
fun Person.Companion.createDefault(): Person {
    return Person("Default Name")
}

fun main() {
    val person = Person.createDefault()
    println(person.name)  // Default Name
}
```

---

## Ответ

### Вопрос
Что такое object / companion object ?

### Ответ
object и companion object используются для реализации различных паттернов и функциональностей, включая паттерн одиночка singleton объявление статических членов и функций а также для реализации объектов без необходимости явного создания экземпляра класса. object используется для создания одиночного экземпляра класса то есть реализации паттерна одиночка singleton. companion object используется внутри класса и служит для объявления членов класса доступных без создания экземпляра этого класса аналогично статическим членам.

---
tags:
  - companion-object
  - const
  - jvmstatic
  - kotlin
  - programming-languages
  - static
difficulty: easy
---

# Как сделать статическую переменную?

**English**: How to create a static variable?

## Answer

Kotlin **does not have** the `static` keyword, but there are several equivalents:

**1. companion object** - Inside class

**2. Top-level declarations** - Outside class

**3. @JvmField / @JvmStatic** - Java interop

**4. const val** - Compile-time constants

**5. object** - Singleton

**1. companion object - Most Common:**

```kotlin
class User {
    companion object {
        // Static-like variable
        var userCount = 0

        // Static-like constant
        const val MAX_AGE = 120

        // Static-like function
        fun createGuest(): User {
            return User("Guest")
        }
    }

    private val name: String

    constructor(name: String) {
        this.name = name
        userCount++  // Access like static
    }
}

// Usage - like static
User.userCount = 0
println(User.MAX_AGE)
val guest = User.createGuest()
```

**2. Top-level Declarations:**

```kotlin
// File: Constants.kt

// Top-level constant - like static
const val API_URL = "https://api.example.com"

// Top-level variable - like static
var requestCount = 0

// Top-level function - like static
fun log(message: String) {
    println("[LOG] $message")
}

// Usage - direct access
println(API_URL)
requestCount++
log("Hello")
```

**3. @JvmField - Java-compatible field:**

```kotlin
class Config {
    companion object {
        // Kotlin access: Config.timeout
        // Java access: Config.timeout (public static field)
        @JvmField
        var timeout = 30
    }
}
```

**4. @JvmStatic - Java-compatible method:**

```kotlin
class Calculator {
    companion object {
        @JvmStatic
        fun add(a: Int, b: Int) = a + b

        // Without @JvmStatic, Java needs: Calculator.Companion.multiply(...)
        fun multiply(a: Int, b: Int) = a * b
    }
}

// Kotlin
Calculator.add(2, 3)
Calculator.multiply(2, 3)

// Java
Calculator.add(2, 3);  // Works with @JvmStatic
Calculator.Companion.multiply(2, 3);  // Without @JvmStatic
```

**5. const val - Compile-time Constants:**

```kotlin
class Constants {
    companion object {
        // Must be primitive or String
        const val MAX_SIZE = 100
        const val APP_NAME = "MyApp"
        const val PI = 3.14159

        // ❌ Cannot use const with computed values
        // const val TIMESTAMP = System.currentTimeMillis()  // Error

        // ✅ Use val instead
        val TIMESTAMP = System.currentTimeMillis()
    }
}
```

**6. object - Singleton with static-like access:**

```kotlin
object DatabaseConfig {
    var host = "localhost"
    var port = 5432

    fun connect() {
        println("Connecting to $host:$port")
    }
}

// Usage - like static
DatabaseConfig.host = "192.168.1.1"
DatabaseConfig.connect()
```

**Comparison:**

| Method | Location | Java Interop | Compile-time |
|--------|----------|--------------|--------------|
| **companion object** | Inside class | Companion.field | No |
| **@JvmField** | companion object | Static field | No |
| **@JvmStatic** | companion object | Static method | No |
| **const val** | companion/top-level | Static final | Yes |
| **Top-level** | Outside class | Static | No |
| **object** | Standalone | Instance | No |

**Complete Example:**

```kotlin
class User(val name: String) {
    companion object {
        // Static constant
        const val DEFAULT_ROLE = "user"

        // Static variable
        private var nextId = 1

        // Static with @JvmField
        @JvmField
        var allowRegistration = true

        // Static with @JvmStatic
        @JvmStatic
        fun generateId(): Int {
            return nextId++
        }

        // Regular companion object member
        fun createAdmin(name: String): User {
            return User(name)
        }
    }

    val id = generateId()
}

// Usage
println(User.DEFAULT_ROLE)  // "user"
User.allowRegistration = false
val id = User.generateId()
val admin = User.createAdmin("Alice")
```

**Java Interop:**

```kotlin
// Kotlin
class MyClass {
    companion object {
        const val CONST = "constant"
        @JvmField var field = "field"
        @JvmStatic fun method() = "method"
        fun regularMethod() = "regular"
    }
}
```

```java
// Java access
String const = MyClass.CONST;  // Direct
String field = MyClass.field;  // Direct with @JvmField
String method = MyClass.method();  // Direct with @JvmStatic
String regular = MyClass.Companion.regularMethod();  // Through Companion
```

**When to Use Each:**

| Use Case | Solution |
|----------|----------|
| Constants | `const val` or `val` in companion |
| Counters, state | `var` in companion object |
| Utility functions | Top-level function or companion object |
| Java interop | `@JvmField`, `@JvmStatic` |
| Singleton | `object` |
| Factory methods | companion object |

**Summary:**

- ❌ **No `static` keyword** in Kotlin
- ✅ **companion object** - most common approach
- ✅ **Top-level** - for file-level constants/functions
- ✅ **@JvmField / @JvmStatic** - Java interop
- ✅ **const val** - compile-time constants
- ✅ **object** - singleton pattern

## Ответ

Kotlin не имеет ключевого слова `static`, но есть эквиваленты:
- Использовать **companion object** внутри класса
- В файле вне классов использовать **@JvmField** или **const val** для констант
- Или создать **object**-синглтон


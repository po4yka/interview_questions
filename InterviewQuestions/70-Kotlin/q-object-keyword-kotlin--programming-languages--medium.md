---
tags:
  - programming-languages
difficulty: medium
status: reviewed
---

# Tell about the Object keyword in Kotlin

**English**: Tell about the Object keyword in Kotlin.

## Answer

The `object` keyword in Kotlin is one of the most powerful and unique features of the language. It has several important applications:

1. **Object declaration (Singleton)** - Creates a single instance that exists throughout the application
2. **Companion objects** - Declares members accessible without creating a class instance (similar to static in Java)
3. **Object expressions** - Creates anonymous objects (similar to anonymous inner classes in Java)
4. **Anonymous objects** - Implements interfaces or extends classes on the fly

**Key characteristics:**
- Thread-safe by default
- Lazily initialized on first access
- Can implement interfaces and inherit from classes
- Can have properties, methods, and init blocks

### Code Examples

**1. Object Declaration (Singleton):**

```kotlin
object DatabaseManager {
    private var connectionCount = 0

    init {
        println("DatabaseManager initialized")
    }

    fun connect(): String {
        connectionCount++
        return "Connection #$connectionCount established"
    }

    fun disconnect() {
        println("Disconnected")
    }

    fun getStats() = "Total connections: $connectionCount"
}

fun main() {
    println(DatabaseManager.connect())  // Connection #1 established
    println(DatabaseManager.connect())  // Connection #2 established
    println(DatabaseManager.getStats())  // Total connections: 2

    DatabaseManager.disconnect()
}
```

**2. Companion Objects:**

```kotlin
class User(val id: Int, val name: String) {
    companion object {
        private var nextId = 1
        const val MIN_NAME_LENGTH = 3

        // Factory method
        fun create(name: String): User {
            require(name.length >= MIN_NAME_LENGTH) {
                "Name must be at least $MIN_NAME_LENGTH characters"
            }
            return User(nextId++, name)
        }

        // Helper method
        fun validateName(name: String): Boolean {
            return name.length >= MIN_NAME_LENGTH
        }
    }

    override fun toString() = "User(id=$id, name=$name)"
}

fun main() {
    val user1 = User.create("Alice")
    val user2 = User.create("Bob")

    println(user1)  // User(id=1, name=Alice)
    println(user2)  // User(id=2, name=Bob)

    println("Is valid: ${User.validateName("Al")}")  // false
}
```

**3. Object Expressions (Anonymous Objects):**

```kotlin
interface ClickListener {
    fun onClick()
    fun onLongClick()
}

fun setClickListener(listener: ClickListener) {
    listener.onClick()
}

fun main() {
    // Anonymous object implementing interface
    setClickListener(object : ClickListener {
        override fun onClick() {
            println("Button clicked!")
        }

        override fun onLongClick() {
            println("Button long-clicked!")
        }
    })

    // Anonymous object extending class
    open class Animal(val name: String) {
        open fun makeSound() {
            println("$name makes a sound")
        }
    }

    val dog = object : Animal("Dog") {
        override fun makeSound() {
            println("$name barks: Woof!")
        }
    }

    dog.makeSound()  // Dog barks: Woof!
}
```

**4. Object Expressions with Multiple Interfaces:**

```kotlin
interface Logger {
    fun log(message: String)
}

interface ErrorHandler {
    fun handleError(error: Exception)
}

fun createLogger(): Logger {
    return object : Logger, ErrorHandler {
        override fun log(message: String) {
            println("[LOG] $message")
        }

        override fun handleError(error: Exception) {
            println("[ERROR] ${error.message}")
        }
    }
}

fun main() {
    val logger = createLogger()
    logger.log("Application started")
}
```

**5. Object with State:**

```kotlin
object AppConfig {
    var apiUrl: String = "https://api.example.com"
    var timeout: Int = 30
    var debugMode: Boolean = false
    private val features = mutableMapOf<String, Boolean>()

    fun enableFeature(name: String) {
        features[name] = true
    }

    fun isFeatureEnabled(name: String): Boolean {
        return features[name] ?: false
    }

    fun printConfig() {
        println("API URL: $apiUrl")
        println("Timeout: $timeout")
        println("Debug Mode: $debugMode")
        println("Features: $features")
    }
}

fun main() {
    AppConfig.apiUrl = "https://api.production.com"
    AppConfig.debugMode = true
    AppConfig.enableFeature("dark_mode")
    AppConfig.enableFeature("notifications")

    AppConfig.printConfig()
    println("Dark mode enabled: ${AppConfig.isFeatureEnabled("dark_mode")}")
}
```

**6. Named Companion Object:**

```kotlin
class MyClass {
    companion object Factory {
        fun create(): MyClass = MyClass()
        fun createWithDefaults(): MyClass = MyClass()
    }
}

fun main() {
    // Can use both ways
    val obj1 = MyClass.create()
    val obj2 = MyClass.Factory.create()
}
```

**7. Object Implementing Interface:**

```kotlin
interface Printer {
    fun print(message: String)
}

object ConsolePrinter : Printer {
    override fun print(message: String) {
        println("[CONSOLE] $message")
    }
}

object FilePrinter : Printer {
    override fun print(message: String) {
        println("[FILE] Writing to file: $message")
    }
}

fun usePrinter(printer: Printer) {
    printer.print("Hello, World!")
}

fun main() {
    usePrinter(ConsolePrinter)
    usePrinter(FilePrinter)
}
```

**8. Anonymous Object with Local Variables:**

```kotlin
fun createCounter(start: Int): Any {
    var count = start

    return object {
        fun increment() = ++count
        fun decrement() = --count
        fun current() = count
    }
}

fun main() {
    val counter = createCounter(10)

    // Note: Need to cast to access methods due to type erasure
    val c = counter as? Any
    // In real code, you'd define an interface
}

// Better approach with interface:
interface Counter {
    fun increment(): Int
    fun decrement(): Int
    fun current(): Int
}

fun createCounterInterface(start: Int): Counter {
    var count = start

    return object : Counter {
        override fun increment() = ++count
        override fun decrement() = --count
        override fun current() = count
    }
}

fun demonstrateCounter() {
    val counter = createCounterInterface(5)
    println(counter.increment())  // 6
    println(counter.increment())  // 7
    println(counter.decrement())  // 6
    println(counter.current())    // 6
}
```

**9. Object as Namespace:**

```kotlin
object MathUtils {
    const val PI = 3.14159265359

    fun square(x: Int) = x * x

    fun cube(x: Int) = x * x * x

    fun isPrime(n: Int): Boolean {
        if (n < 2) return false
        for (i in 2..Math.sqrt(n.toDouble()).toInt()) {
            if (n % i == 0) return false
        }
        return true
    }
}

fun main() {
    println("Square of 5: ${MathUtils.square(5)}")
    println("Cube of 3: ${MathUtils.cube(3)}")
    println("Is 17 prime: ${MathUtils.isPrime(17)}")
    println("PI: ${MathUtils.PI}")
}
```

**10. Object vs Class Instance:**

```kotlin
// Regular class - multiple instances
class RegularClass {
    val id = System.currentTimeMillis()
}

// Object - single instance
object SingletonObject {
    val id = System.currentTimeMillis()
}

fun main() {
    val r1 = RegularClass()
    Thread.sleep(10)
    val r2 = RegularClass()

    println("Regular instances same? ${r1 === r2}")  // false
    println("R1 ID: ${r1.id}")
    println("R2 ID: ${r2.id}")  // Different IDs

    println()

    val s1 = SingletonObject
    Thread.sleep(10)
    val s2 = SingletonObject

    println("Singleton instances same? ${s1 === s2}")  // true
    println("S1 ID: ${s1.id}")
    println("S2 ID: ${s2.id}")  // Same ID
}
```

---

## Ответ

### Вопрос
Расскажи про ключевое слово Object в Kotlin

### Ответ
Ключевое слово object в Kotlin имеет несколько важных применений и является одной из наиболее мощных и уникальных возможностей языка. Оно используется для объявления объекта-одиночки (Singleton), анонимных объектов, компаньон-объектов и объект-выражений.

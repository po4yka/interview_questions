---
tags:
  - programming-languages
difficulty: easy
status: draft
---

# How to create a singleton in Kotlin?

**English**: How to create a singleton in Kotlin?

## Answer

In Kotlin, you can create a singleton using an object declaration. This is the simplest and most idiomatic way to implement the Singleton pattern in Kotlin.

**Syntax:**
```kotlin
object MySingleton {
    // properties and methods
}
```

**Key features:**
- Thread-safe by default (no need for synchronization)
- Lazily initialized when first accessed
- Only one instance exists throughout the application
- Cannot have constructors
- Can have properties, methods, and init blocks
- Can inherit from classes and implement interfaces

### Code Examples

**Basic singleton:**
```kotlin
object AppConfig {
    var apiUrl = "https://api.example.com"
    var timeout = 30
    var debugMode = false

    fun printConfig() {
        println("API URL: $apiUrl")
        println("Timeout: $timeout")
        println("Debug Mode: $debugMode")
    }
}

fun main() {
    // Direct access without instantiation
    AppConfig.apiUrl = "https://api.production.com"
    AppConfig.debugMode = true
    AppConfig.printConfig()

    // Always the same instance
    val config1 = AppConfig
    val config2 = AppConfig
    println(config1 === config2)  // true
}
```

**Singleton with initialization:**
```kotlin
object DatabaseManager {
    private val connections = mutableListOf<String>()

    init {
        println("DatabaseManager initialized")
        // Perform initialization
        connections.add("Default Connection")
    }

    fun addConnection(name: String) {
        connections.add(name)
    }

    fun getConnections(): List<String> = connections
}

fun main() {
    // First access triggers initialization
    println("Before first access")
    DatabaseManager.addConnection("Connection 1")  // DatabaseManager initialized
    DatabaseManager.addConnection("Connection 2")

    println(DatabaseManager.getConnections())
}
```

**Singleton implementing interface:**
```kotlin
interface Logger {
    fun log(message: String)
    fun error(message: String)
}

object ConsoleLogger : Logger {
    override fun log(message: String) {
        println("[LOG] $message")
    }

    override fun error(message: String) {
        println("[ERROR] $message")
    }
}

fun main() {
    ConsoleLogger.log("Application started")
    ConsoleLogger.error("An error occurred")
}
```

**Singleton with properties and methods:**
```kotlin
object UserSession {
    var userId: String? = null
    var username: String? = null
    var isLoggedIn: Boolean = false

    fun login(id: String, name: String) {
        userId = id
        username = name
        isLoggedIn = true
        println("User $name logged in")
    }

    fun logout() {
        println("User $username logged out")
        userId = null
        username = null
        isLoggedIn = false
    }

    fun getCurrentUser(): String? = username
}

fun main() {
    UserSession.login("123", "Alice")
    println("Current user: ${UserSession.getCurrentUser()}")
    println("Is logged in: ${UserSession.isLoggedIn}")

    UserSession.logout()
    println("Is logged in: ${UserSession.isLoggedIn}")
}
```

**Alternative: Singleton using companion object (for lazy initialization with parameters):**
```kotlin
class DatabaseConnection private constructor(val url: String) {
    companion object {
        @Volatile
        private var instance: DatabaseConnection? = null

        fun getInstance(url: String): DatabaseConnection {
            return instance ?: synchronized(this) {
                instance ?: DatabaseConnection(url).also { instance = it }
            }
        }
    }

    fun connect() {
        println("Connecting to $url")
    }
}

fun main() {
    val db1 = DatabaseConnection.getInstance("jdbc:mysql://localhost:3306")
    val db2 = DatabaseConnection.getInstance("jdbc:mysql://localhost:3306")

    println(db1 === db2)  // true
    db1.connect()
}
```

**Thread-safety demonstration:**
```kotlin
object Counter {
    private var count = 0

    fun increment() {
        count++
    }

    fun getCount() = count
}

fun main() {
    // Safe to use from multiple threads
    val threads = List(10) {
        Thread {
            repeat(1000) {
                Counter.increment()
            }
        }
    }

    threads.forEach { it.start() }
    threads.forEach { it.join() }

    println("Final count: ${Counter.getCount()}")  // 10000
}
```

---

## Ответ

### Вопрос
Как в Kotlin можно создать синглтон

### Ответ
В Kotlin можно создать singleton, используя object-декларацию. Пример: object MySingleton { // свойства и методы }

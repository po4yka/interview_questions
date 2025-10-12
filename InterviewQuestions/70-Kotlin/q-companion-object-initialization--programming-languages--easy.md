---
tags:
  - programming-languages
difficulty: easy
status: draft
---

# When is companion object initialized?

# Question (EN)
> When is a companion object initialized in Kotlin?

# Вопрос (RU)
> Когда инициализируется companion object в Kotlin?

---

## Answer (EN)

A companion object is initialized **lazily when first accessed**. It is initialized on the first access to any of its members (properties or functions), including when the companion object itself is referenced.

**Key points:**
- Initialized on first access (lazy initialization)
- Thread-safe by default
- Initialized only once throughout the application lifecycle
- Initialization happens before the first use of any companion member
- Similar to Java static initializer blocks

**Not initialized when:**
- Just creating an instance of the containing class (if companion members aren't accessed)
- Class is loaded but companion object members aren't used

### Code Examples

**Basic initialization timing:**

```kotlin
class MyClass {
    companion object {
        init {
            println("Companion object initialized!")
        }

        val value = "Hello"
    }

    init {
        println("MyClass instance created!")
    }
}

fun main() {
    println("Before creating instance")
    val instance = MyClass()
    // Output:
    // Before creating instance
    // MyClass instance created!

    println("\nBefore accessing companion")
    println(MyClass.value)
    // Output:
    // Before accessing companion
    // Companion object initialized!
    // Hello

    println("\nAccessing companion again")
    println(MyClass.value)
    // Output:
    // Accessing companion again
    // Hello
    // (No initialization message - already initialized)
}
```

**Companion object initialization with properties:**

```kotlin
class Database {
    companion object {
        private var connectionCount = 0

        init {
            println("Initializing Database companion object...")
            connectionCount = 0
        }

        fun connect(): String {
            connectionCount++
            return "Connection #$connectionCount established"
        }

        fun getStats(): String {
            return "Total connections: $connectionCount"
        }
    }
}

fun main() {
    println("Starting application...")

    // Companion object NOT initialized yet
    val db1 = Database()
    println("Created Database instance")

    // First access - companion object initialized here
    println("\nFirst companion access:")
    println(Database.connect())
    // Initializing Database companion object...
    // Connection #1 established

    // Already initialized
    println("\nSecond companion access:")
    println(Database.connect())
    // Connection #2 established

    println(Database.getStats())
    // Total connections: 2
}
```

**Multiple class instances vs single companion:**

```kotlin
class Counter(val instanceId: Int) {
    companion object {
        private var instanceCount = 0
        private val creationTime = System.currentTimeMillis()

        init {
            println("Companion object initialized at $creationTime")
        }

        fun getInstanceCount() = instanceCount
        fun getCreationTime() = creationTime
    }

    init {
        companion object.instanceCount++
        println("Instance #$instanceId created (total: ${companion object.instanceCount})")
    }
}

fun main() {
    println("Creating first instance:")
    val c1 = Counter(1)
    // Companion object initialized at 1696348800000
    // Instance #1 created (total: 1)

    println("\nCreating second instance:")
    val c2 = Counter(2)
    // Instance #2 created (total: 2)
    // (Companion already initialized)

    println("\nCreating third instance:")
    val c3 = Counter(3)
    // Instance #3 created (total: 3)

    println("\nTotal instances: ${Counter.getInstanceCount()}")
    // Total instances: 3
}
```

**Lazy initialization demonstration:**

```kotlin
class ExpensiveResource {
    companion object {
        init {
            println("Loading expensive resources...")
            Thread.sleep(1000)  // Simulate expensive operation
            println("Resources loaded!")
        }

        fun doSomething() {
            println("Doing something with resources")
        }
    }

    init {
        println("ExpensiveResource instance created")
    }
}

fun main() {
    println("Application started")

    println("\nCreating instances...")
    val r1 = ExpensiveResource()
    val r2 = ExpensiveResource()
    // Companion NOT initialized yet - expensive operation avoided

    println("\nNow accessing companion for first time...")
    ExpensiveResource.doSomething()
    // Loading expensive resources...
    // (1 second delay)
    // Resources loaded!
    // Doing something with resources

    println("\nAccessing companion again...")
    ExpensiveResource.doSomething()
    // Doing something with resources
    // (No delay - already initialized)
}
```

**Initialization order with inheritance:**

```kotlin
open class Base {
    companion object {
        init {
            println("Base companion initialized")
        }

        val baseValue = "Base"
    }

    init {
        println("Base instance created")
    }
}

class Derived : Base() {
    companion object {
        init {
            println("Derived companion initialized")
        }

        val derivedValue = "Derived"
    }

    init {
        println("Derived instance created")
    }
}

fun main() {
    println("Creating Derived instance:")
    val d = Derived()
    // Base instance created
    // Derived instance created
    // (No companion initialized)

    println("\nAccessing Base companion:")
    println(Base.baseValue)
    // Base companion initialized
    // Base

    println("\nAccessing Derived companion:")
    println(Derived.derivedValue)
    // Derived companion initialized
    // Derived
}
```

**Factory pattern with lazy companion:**

```kotlin
class User private constructor(val id: Int, val name: String) {
    companion object {
        private val users = mutableMapOf<Int, User>()
        private var nextId = 1

        init {
            println("User companion object initialized")
            println("User factory ready")
        }

        fun create(name: String): User {
            val user = User(nextId++, name)
            users[user.id] = user
            return user
        }

        fun getById(id: Int): User? = users[id]

        fun getAllUsers(): List<User> = users.values.toList()
    }
}

fun main() {
    println("Application started")

    // Companion initialized on first use
    println("\nCreating first user:")
    val user1 = User.create("Alice")
    // User companion object initialized
    // User factory ready

    println("User created: ${user1.name} (ID: ${user1.id})")

    // Already initialized
    val user2 = User.create("Bob")
    println("User created: ${user2.name} (ID: ${user2.id})")

    println("\nAll users: ${User.getAllUsers().map { it.name }}")
}
```

**Thread-safe initialization:**

```kotlin
class ThreadSafeExample {
    companion object {
        private var initializationThread: String? = null

        init {
            initializationThread = Thread.currentThread().name
            println("Initialized by thread: $initializationThread")
        }

        fun getInitThread() = initializationThread
    }
}

fun main() {
    // Create multiple threads trying to access companion
    val threads = List(10) { index ->
        Thread {
            println("Thread $index accessing companion")
            ThreadSafeExample.getInitThread()
        }
    }

    threads.forEach { it.start() }
    threads.forEach { it.join() }

    // Only initialized once by first thread to access it
    println("\nInitialized by: ${ThreadSafeExample.getInitThread()}")
}
```

**Avoiding premature initialization:**

```kotlin
class ConfigManager {
    companion object {
        init {
            println("Loading configuration from file...")
            Thread.sleep(500)  // Simulate file I/O
            println("Configuration loaded!")
        }

        val config = mapOf(
            "api_url" to "https://api.example.com",
            "timeout" to "30",
            "debug" to "true"
        )

        fun get(key: String): String? = config[key]
    }
}

fun main() {
    println("App starting...")

    // Do other work - companion not initialized yet
    println("Doing some work...")
    repeat(3) { i ->
        println("  Step ${i + 1}")
        Thread.sleep(200)
    }

    // Now we need config - initialized here
    println("\nNeed configuration now:")
    val apiUrl = ConfigManager.get("api_url")
    println("API URL: $apiUrl")
}
```

---

## Ответ (RU)

Companion object инициализируется **лениво при первом доступе**. Он инициализируется при первом обращении к любому из его членов (свойствам или функциям), включая случаи, когда происходит обращение к самому companion object.

**Ключевые моменты:**
- Инициализация при первом доступе (ленивая инициализация)
- Потокобезопасна по умолчанию
- Инициализируется только один раз за весь жизненный цикл приложения
- Инициализация происходит до первого использования любого члена companion
- Аналогично статическим блокам инициализации в Java

**НЕ инициализируется когда:**
- Просто создается экземпляр содержащего класса (если члены companion не используются)
- Класс загружен, но члены companion object не используются

### Пример базовой инициализации

```kotlin
class MyClass {
    companion object {
        init {
            println("Companion object initialized!")
        }
        val value = "Hello"
    }

    init {
        println("MyClass instance created!")
    }
}

fun main() {
    val instance = MyClass()  // Выведет: "MyClass instance created!"
    println(MyClass.value)     // Выведет: "Companion object initialized!" затем "Hello"
    println(MyClass.value)     // Выведет только: "Hello" (уже инициализирован)
}
```

### Важные особенности

1. **Один companion на все экземпляры** - companion object инициализируется один раз, независимо от количества созданных экземпляров класса

2. **Ленивая загрузка** - если companion object содержит дорогостоящие операции, они не выполнятся, пока не понадобятся

3. **Потокобезопасность** - инициализация гарантированно произойдет только один раз, даже при многопоточном доступе

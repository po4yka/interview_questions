---
id: 20251012-144303
title: "Kotlin Constructors / Конструкторы в Kotlin"
aliases: []

# Classification
topic: kotlin
subtopics: [constructors, primary-constructor, secondary-constructor, init-block, initialization]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive guide on Kotlin constructors

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-kotlin-init-block--kotlin--easy, q-kotlin-properties--kotlin--easy, q-kotlin-val-vs-var--kotlin--easy]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [kotlin, constructors, primary-constructor, secondary-constructor, init, initialization, difficulty/easy]
---

# Question (EN)
> What are constructors in Kotlin? Explain primary constructors, secondary constructors, and init blocks.

# Вопрос (RU)
> Что такое конструкторы в Kotlin? Объясните первичные конструкторы, вторичные конструкторы и блоки init.

---

## Answer (EN)

Kotlin has **primary constructors** and **secondary constructors** for initializing class instances. Unlike Java, Kotlin separates constructor parameters from initialization logic, providing a cleaner and more flexible approach to object creation.

### Key Concepts

1. **Primary Constructor**: Declared in the class header, cannot contain code
2. **Secondary Constructor**: Defined in the class body with the `constructor` keyword
3. **Init Blocks**: Execute initialization code, run as part of the primary constructor
4. **Constructor Parameters vs Properties**: Parameters can become properties using `val`/`var`
5. **Default Values**: Constructor parameters can have default values
6. **Named Arguments**: Make constructor calls more readable

### Primary Constructor

The primary constructor is part of the class header, declared after the class name:

```kotlin
// Basic primary constructor
class Person(name: String, age: Int) {
    val name: String = name
    val age: Int = age
}

// Shorter syntax - parameters become properties
class Person(val name: String, val age: Int)

// With visibility modifier
class Person private constructor(val name: String, val age: Int)

// Usage
val person = Person("Alice", 25)
println("${person.name} is ${person.age} years old")
```

**Key Points**:
- Declared in class header after class name
- Cannot contain any code (use init blocks instead)
- Parameters can be declared as properties using `val`/`var`
- Can have visibility modifiers (`private`, `protected`, `internal`)

### Constructor Parameters as Properties

```kotlin
// Parameter only (not a property)
class Person(name: String) {
    val personName = name.uppercase()
    // 'name' is not accessible as a property
}

// Parameter becomes a property
class Person(val name: String) {
    // 'name' is accessible as person.name
}

// Mutable property
class Person(var name: String) {
    // 'name' can be modified: person.name = "Bob"
}

// Mixed approach
class User(
    val id: Int,           // Property
    var username: String,  // Mutable property
    email: String          // Parameter only
) {
    val emailDomain = email.substringAfter("@")
}

val user = User(1, "alice", "alice@example.com")
println(user.username)      // OK
// println(user.email)      // Error: email is not a property
```

### Init Blocks

Init blocks execute initialization code as part of the primary constructor:

```kotlin
class Person(val name: String, val age: Int) {
    init {
        println("Creating person: $name")
        require(age >= 0) { "Age cannot be negative" }
    }
}

// Multiple init blocks execute in order
class User(val username: String) {
    val createdAt: Long

    init {
        println("First init: validating username")
        require(username.isNotBlank()) { "Username cannot be blank" }
    }

    val id = generateId()

    init {
        println("Second init: setting timestamp")
        createdAt = System.currentTimeMillis()
    }

    private fun generateId(): String =
        "${username.hashCode()}-${System.currentTimeMillis()}"
}

// Execution order:
// 1. Primary constructor parameters
// 2. Property initializers and init blocks (in declaration order)
```

### Default Values

Constructor parameters can have default values:

```kotlin
class User(
    val username: String,
    val email: String = "",
    val age: Int = 0,
    val isActive: Boolean = true
) {
    override fun toString() =
        "User(username=$username, email=$email, age=$age, active=$isActive)"
}

// Usage with default values
val user1 = User("alice")
val user2 = User("bob", "bob@example.com")
val user3 = User("charlie", age = 30)
val user4 = User("david", email = "david@test.com", age = 25, isActive = false)

println(user1)  // User(username=alice, email=, age=0, active=true)
println(user2)  // User(username=bob, email=bob@example.com, age=0, active=true)
```

### Named Arguments

Named arguments make constructor calls more readable:

```kotlin
class Rectangle(
    val width: Int,
    val height: Int,
    val color: String = "black",
    val filled: Boolean = false
)

// Positional arguments
val rect1 = Rectangle(100, 50, "red", true)

// Named arguments (any order)
val rect2 = Rectangle(
    height = 50,
    width = 100,
    filled = true,
    color = "blue"
)

// Mix of positional and named
val rect3 = Rectangle(100, 50, filled = true)
```

### Secondary Constructors

Secondary constructors provide alternative ways to create instances:

```kotlin
class Person(val name: String, val age: Int) {
    var email: String = ""

    // Secondary constructor must delegate to primary
    constructor(name: String, age: Int, email: String) : this(name, age) {
        this.email = email
        println("Secondary constructor called")
    }
}

// Usage
val person1 = Person("Alice", 25)
val person2 = Person("Bob", 30, "bob@example.com")
```

### Multiple Secondary Constructors

```kotlin
class User(val id: Int, val username: String) {
    var email: String = ""
    var phone: String = ""

    init {
        println("Primary constructor")
    }

    // Secondary constructor 1
    constructor(id: Int, username: String, email: String) : this(id, username) {
        this.email = email
        println("Secondary constructor 1")
    }

    // Secondary constructor 2
    constructor(id: Int, username: String, email: String, phone: String)
        : this(id, username, email) {
        this.phone = phone
        println("Secondary constructor 2")
    }
}

// Execution order for User(1, "alice", "a@test.com", "123"):
// 1. Primary constructor
// 2. Init blocks
// 3. Secondary constructor 1
// 4. Secondary constructor 2
```

### Class Without Primary Constructor

```kotlin
class Database {
    private var connection: Connection? = null

    // Secondary constructor 1
    constructor(url: String) {
        connection = DriverManager.getConnection(url)
    }

    // Secondary constructor 2
    constructor(url: String, user: String, password: String) {
        connection = DriverManager.getConnection(url, user, password)
    }
}

val db1 = Database("jdbc:sqlite:test.db")
val db2 = Database("jdbc:mysql://localhost/test", "root", "password")
```

### Real-World Example: Configuration Class

```kotlin
class DatabaseConfig(
    val host: String,
    val port: Int = 5432,
    val database: String,
    val username: String = "postgres",
    val password: String = "",
    val sslEnabled: Boolean = true,
    val maxConnections: Int = 10
) {
    val connectionUrl: String

    init {
        require(host.isNotBlank()) { "Host cannot be blank" }
        require(port in 1..65535) { "Port must be between 1 and 65535" }
        require(database.isNotBlank()) { "Database name cannot be blank" }
        require(maxConnections > 0) { "Max connections must be positive" }

        connectionUrl = buildConnectionUrl()
    }

    // Secondary constructor for local development
    constructor(database: String) : this(
        host = "localhost",
        database = database,
        username = "postgres",
        password = "postgres"
    )

    private fun buildConnectionUrl(): String {
        val protocol = if (sslEnabled) "postgresql+ssl" else "postgresql"
        return "$protocol://$host:$port/$database"
    }

    override fun toString() = """
        DatabaseConfig(
            host=$host,
            port=$port,
            database=$database,
            connectionUrl=$connectionUrl,
            maxConnections=$maxConnections
        )
    """.trimIndent()
}

// Usage
val prodConfig = DatabaseConfig(
    host = "prod-db.example.com",
    database = "app_db",
    username = "app_user",
    password = "secret",
    maxConnections = 50
)

val devConfig = DatabaseConfig("dev_db")
```

### Data Classes with Constructors

```kotlin
data class User(
    val id: Int,
    val username: String,
    val email: String,
    val createdAt: Long = System.currentTimeMillis()
) {
    init {
        require(username.length >= 3) { "Username too short" }
        require(email.contains("@")) { "Invalid email" }
    }

    // Secondary constructor
    constructor(username: String, email: String) : this(
        id = username.hashCode(),
        username = username,
        email = email
    )
}

val user1 = User(1, "alice", "alice@example.com")
val user2 = User("bob", "bob@example.com")
```

### Constructor Visibility

```kotlin
// Private primary constructor
class Singleton private constructor(val name: String) {
    companion object {
        private var instance: Singleton? = null

        fun getInstance(name: String): Singleton {
            return instance ?: synchronized(this) {
                instance ?: Singleton(name).also { instance = it }
            }
        }
    }
}

val singleton = Singleton.getInstance("MyApp")

// Internal constructor
internal class InternalService internal constructor(val config: Config)

// Protected constructor (in abstract class)
abstract class BaseRepository protected constructor(val database: Database)
```

### Best Practices

#### DO:
```kotlin
// Use primary constructor with property declarations
class Person(val name: String, val age: Int)

// Use default values for optional parameters
class Config(val timeout: Int = 5000, val retries: Int = 3)

// Use init blocks for validation
class Email(val address: String) {
    init {
        require(address.contains("@")) { "Invalid email" }
    }
}

// Use named arguments for clarity
val rect = Rectangle(width = 100, height = 50, color = "red")

// Use secondary constructors for alternative construction patterns
class User(val id: Int, val name: String) {
    constructor(name: String) : this(name.hashCode(), name)
}
```

#### DON'T:
```kotlin
// Don't repeat property declarations
class Person(name: String, age: Int) {  // Parameters
    val name: String = name              // Unnecessary
    val age: Int = age                   // Unnecessary
}
// Instead: class Person(val name: String, val age: Int)

// Don't use secondary constructors when default values work
class User(val name: String, val age: Int) {
    constructor(name: String) : this(name, 0)  // Bad
}
// Instead: class User(val name: String, val age: Int = 0)

// Don't put complex logic in init blocks
class Service(val config: Config) {
    init {
        // Avoid heavy computations or I/O here
        connectToDatabase()  // Bad: should be explicit
    }
}

// Don't skip validation in constructors
class Age(val value: Int)  // Bad: no validation
// Instead:
class Age(val value: Int) {
    init {
        require(value >= 0) { "Age cannot be negative" }
    }
}
```

### Common Patterns

#### Factory Pattern with Private Constructor

```kotlin
class User private constructor(
    val id: Int,
    val username: String,
    val email: String
) {
    companion object {
        fun create(username: String, email: String): User {
            val id = generateId()
            return User(id, username, email)
        }

        fun fromDatabase(id: Int, username: String, email: String): User {
            return User(id, username, email)
        }

        private fun generateId(): Int =
            (System.currentTimeMillis() % Int.MAX_VALUE).toInt()
    }
}

val user = User.create("alice", "alice@example.com")
```

#### Builder Pattern

```kotlin
class HttpRequest private constructor(
    val url: String,
    val method: String,
    val headers: Map<String, String>,
    val body: String?
) {
    class Builder {
        private var url: String = ""
        private var method: String = "GET"
        private val headers = mutableMapOf<String, String>()
        private var body: String? = null

        fun url(url: String) = apply { this.url = url }
        fun method(method: String) = apply { this.method = method }
        fun header(key: String, value: String) = apply {
            headers[key] = value
        }
        fun body(body: String) = apply { this.body = body }

        fun build(): HttpRequest {
            require(url.isNotBlank()) { "URL is required" }
            return HttpRequest(url, method, headers, body)
        }
    }
}

val request = HttpRequest.Builder()
    .url("https://api.example.com/users")
    .method("POST")
    .header("Content-Type", "application/json")
    .body("""{"name":"Alice"}""")
    .build()
```

---

## Ответ (RU)

Kotlin имеет **первичные конструкторы** и **вторичные конструкторы** для инициализации экземпляров классов. В отличие от Java, Kotlin разделяет параметры конструктора и логику инициализации, обеспечивая более чистый и гибкий подход к созданию объектов.

### Ключевые концепции

1. **Первичный конструктор**: Объявляется в заголовке класса, не может содержать код
2. **Вторичный конструктор**: Определяется в теле класса с ключевым словом `constructor`
3. **Блоки Init**: Выполняют код инициализации, работают как часть первичного конструктора
4. **Параметры конструктора vs Свойства**: Параметры могут стать свойствами используя `val`/`var`
5. **Значения по умолчанию**: Параметры конструктора могут иметь значения по умолчанию
6. **Именованные аргументы**: Делают вызовы конструктора более читаемыми

### Первичный конструктор

Первичный конструктор является частью заголовка класса:

```kotlin
// Базовый первичный конструктор
class Person(name: String, age: Int) {
    val name: String = name
    val age: Int = age
}

// Короткий синтаксис - параметры становятся свойствами
class Person(val name: String, val age: Int)

// С модификатором видимости
class Person private constructor(val name: String, val age: Int)

// Использование
val person = Person("Alice", 25)
println("${person.name} is ${person.age} years old")
```

### Параметры конструктора как свойства

```kotlin
// Только параметр (не свойство)
class Person(name: String) {
    val personName = name.uppercase()
    // 'name' не доступен как свойство
}

// Параметр становится свойством
class Person(val name: String) {
    // 'name' доступен как person.name
}

// Изменяемое свойство
class Person(var name: String) {
    // 'name' можно изменить: person.name = "Bob"
}

// Смешанный подход
class User(
    val id: Int,           // Свойство
    var username: String,  // Изменяемое свойство
    email: String          // Только параметр
) {
    val emailDomain = email.substringAfter("@")
}
```

### Блоки Init

Блоки init выполняют код инициализации как часть первичного конструктора:

```kotlin
class Person(val name: String, val age: Int) {
    init {
        println("Создание персоны: $name")
        require(age >= 0) { "Возраст не может быть отрицательным" }
    }
}

// Множественные блоки init выполняются по порядку
class User(val username: String) {
    val createdAt: Long

    init {
        println("Первый init: валидация username")
        require(username.isNotBlank()) { "Username не может быть пустым" }
    }

    val id = generateId()

    init {
        println("Второй init: установка timestamp")
        createdAt = System.currentTimeMillis()
    }

    private fun generateId(): String =
        "${username.hashCode()}-${System.currentTimeMillis()}"
}
```

### Значения по умолчанию

```kotlin
class User(
    val username: String,
    val email: String = "",
    val age: Int = 0,
    val isActive: Boolean = true
)

// Использование со значениями по умолчанию
val user1 = User("alice")
val user2 = User("bob", "bob@example.com")
val user3 = User("charlie", age = 30)
```

### Вторичные конструкторы

Вторичные конструкторы предоставляют альтернативные способы создания экземпляров:

```kotlin
class Person(val name: String, val age: Int) {
    var email: String = ""

    // Вторичный конструктор должен делегировать первичному
    constructor(name: String, age: Int, email: String) : this(name, age) {
        this.email = email
        println("Вызван вторичный конструктор")
    }
}

// Использование
val person1 = Person("Alice", 25)
val person2 = Person("Bob", 30, "bob@example.com")
```

### Множественные вторичные конструкторы

```kotlin
class User(val id: Int, val username: String) {
    var email: String = ""
    var phone: String = ""

    init {
        println("Первичный конструктор")
    }

    // Вторичный конструктор 1
    constructor(id: Int, username: String, email: String) : this(id, username) {
        this.email = email
        println("Вторичный конструктор 1")
    }

    // Вторичный конструктор 2
    constructor(id: Int, username: String, email: String, phone: String)
        : this(id, username, email) {
        this.phone = phone
        println("Вторичный конструктор 2")
    }
}

// Порядок выполнения для User(1, "alice", "a@test.com", "123"):
// 1. Первичный конструктор
// 2. Блоки Init
// 3. Вторичный конструктор 1
// 4. Вторичный конструктор 2
```

### Лучшие практики

#### ДЕЛАТЬ:
```kotlin
// Использовать первичный конструктор с объявлениями свойств
class Person(val name: String, val age: Int)

// Использовать значения по умолчанию для опциональных параметров
class Config(val timeout: Int = 5000, val retries: Int = 3)

// Использовать блоки init для валидации
class Email(val address: String) {
    init {
        require(address.contains("@")) { "Неверный email" }
    }
}
```

#### НЕ ДЕЛАТЬ:
```kotlin
// Не повторять объявления свойств
class Person(name: String, age: Int) {
    val name: String = name  // Лишнее
    val age: Int = age       // Лишнее
}

// Не использовать вторичные конструкторы когда работают значения по умолчанию
class User(val name: String, val age: Int) {
    constructor(name: String) : this(name, 0)  // Плохо
}
// Вместо: class User(val name: String, val age: Int = 0)
```

---

## References

- [Kotlin Classes and Inheritance](https://kotlinlang.org/docs/classes.html)
- [Kotlin Constructors](https://kotlinlang.org/docs/classes.html#constructors)
- [Kotlin Properties](https://kotlinlang.org/docs/properties.html)

## Related Questions

- [[q-kotlin-init-block--kotlin--easy]]
- [[q-kotlin-properties--kotlin--easy]]
- [[q-kotlin-val-vs-var--kotlin--easy]]
- [[q-data-class-requirements--programming-languages--medium]]

## MOC Links

- [[moc-kotlin]]

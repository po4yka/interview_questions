---
id: kotlin-088
title: Kotlin Constructors / Конструкторы в Kotlin
aliases:
- Kotlin Constructors
- Конструкторы в Kotlin
topic: kotlin
subtopics:
- constructors
- init-block
- initialization
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
source: internal
source_note: Comprehensive guide on Kotlin constructors
status: draft
moc: moc-kotlin
related:
- c-kotlin
- q-kotlin-init-block--kotlin--easy
- q-kotlin-properties--kotlin--easy
- q-kotlin-val-vs-var--kotlin--easy
created: 2025-10-12
updated: 2025-11-09
tags:
- constructors
- difficulty/easy
- init
- initialization
- kotlin
- primary-constructor
- secondary-constructor
anki_cards:
- slug: kotlin-088-0-en
  language: en
  difficulty: 0.3
  tags:
  - Kotlin
  - difficulty::easy
  - constructors
  - init-block
  - initialization
- slug: kotlin-088-0-ru
  language: ru
  difficulty: 0.3
  tags:
  - Kotlin
  - difficulty::easy
  - constructors
  - init-block
  - initialization
---
# Вопрос (RU)
> Что такое конструкторы в Kotlin? Объясните первичные конструкторы, вторичные конструкторы и блоки init.

# Question (EN)
> What are constructors in Kotlin? Explain primary constructors, secondary constructors, and init blocks.

## Ответ (RU)

Kotlin имеет **первичные конструкторы** и **вторичные конструкторы** для инициализации экземпляров классов. В отличие от Java, Kotlin разделяет параметры конструктора и логику инициализации, обеспечивая более чистый и гибкий подход к созданию объектов. Подробности см. также в [[c-kotlin]].

### Ключевые Концепции

1. **Первичный конструктор**: Объявляется в заголовке класса, не может содержать исполняемый код (логика инициализации выносится в `init`-блоки или инициализаторы свойств)
2. **Вторичный конструктор**: Определяется в теле класса с ключевым словом `constructor`
3. **Блоки init**: Выполняют код инициализации, выполняются вместе с инициализаторами свойств как часть первичного конструктора в порядке объявления
4. **Параметры конструктора vs Свойства**: Параметры могут стать свойствами, если объявлены с `val`/`var`
5. **Значения по умолчанию**: Параметры конструктора могут иметь значения по умолчанию
6. **Именованные аргументы**: Делают вызовы конструктора более читаемыми

### Первичный Конструктор

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

Ключевые моменты:
- Объявляется в заголовке класса после имени
- Не содержит исполняемый код (используйте `init`-блоки)
- Параметры могут быть объявлены как свойства через `val`/`var`
- Может иметь модификаторы видимости (`private`, `protected`, `internal`)

### Параметры Конструктора Как Свойства

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

val user = User(1, "alice", "alice@example.com")
println(user.username)      // OK
// println(user.email)      // Ошибка: email не является свойством
```

### Блоки Init

Блоки `init` выполняют код инициализации как часть первичного конструктора. Они вызываются вместе с инициализаторами свойств в порядке их объявления в классе.

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

// Порядок выполнения:
// 1. Параметры первичного конструктора
// 2. Инициализаторы свойств и блоки init (в порядке объявления)
```

### Значения По Умолчанию

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

// Использование со значениями по умолчанию
val user1 = User("alice")
val user2 = User("bob", "bob@example.com")
val user3 = User("charlie", age = 30)
val user4 = User("david", email = "david@test.com", age = 25, isActive = false)
```

### Именованные Аргументы

Именованные аргументы делают вызовы конструктора более читаемыми и позволяют передавать параметры в любом порядке (после позиционных без пропусков).

```kotlin
class Rectangle(
    val width: Int,
    val height: Int,
    val color: String = "black",
    val filled: Boolean = false
)

// Позиционные аргументы
val rect1 = Rectangle(100, 50, "red", true)

// Именованные аргументы (в любом порядке)
val rect2 = Rectangle(
    height = 50,
    width = 100,
    filled = true,
    color = "blue"
)

// Смешанный подход
val rect3 = Rectangle(100, 50, filled = true)
```

### Вторичные Конструкторы

Вторичные конструкторы предоставляют альтернативные способы создания экземпляров и всегда должны делегировать вызов первичному конструктору (непосредственно или через другой вторичный).

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

### Множественные Вторичные Конструкторы

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
// 1. Первичный конструктор (параметры)
// 2. Инициализаторы свойств и блоки init (в порядке объявления)
// 3. Тело вторичного конструктора 1
// 4. Тело вторичного конструктора 2
```

### Класс Без Первичного Конструктора

Класс может быть объявлен без первичного конструктора и иметь только вторичные.

```kotlin
class Database {
    private var connection: Connection? = null

    // Вторичный конструктор 1
    constructor(url: String) {
        connection = DriverManager.getConnection(url)
    }

    // Вторичный конструктор 2
    constructor(url: String, user: String, password: String) {
        connection = DriverManager.getConnection(url, user, password)
    }
}

val db1 = Database("jdbc:sqlite:test.db")
val db2 = Database("jdbc:mysql://localhost/test", "root", "password")
```

### Реальный Пример: Конфигурационный Класс

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
        require(host.isNotBlank()) { "Host не может быть пустым" }
        require(port in 1..65535) { "Port должен быть в диапазоне 1..65535" }
        require(database.isNotBlank()) { "Имя базы данных не может быть пустым" }
        require(maxConnections > 0) { "Max connections должно быть положительным" }

        connectionUrl = buildConnectionUrl()
    }

    // Вторичный конструктор для локальной разработки
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

// Использование
val prodConfig = DatabaseConfig(
    host = "prod-db.example.com",
    database = "app_db",
    username = "app_user",
    password = "secret",
    maxConnections = 50
)

val devConfig = DatabaseConfig("dev_db")
```

### Data-классы И Конструкторы

```kotlin
data class User(
    val id: Int,
    val username: String,
    val email: String,
    val createdAt: Long = System.currentTimeMillis()
) {
    init {
        require(username.length >= 3) { "Слишком короткий username" }
        require(email.contains("@")) { "Неверный email" }
    }

    // Вторичный конструктор
    constructor(username: String, email: String) : this(
        id = username.hashCode(),
        username = username,
        email = email
    )
}

val user1 = User(1, "alice", "alice@example.com")
val user2 = User("bob", "bob@example.com")
```

### Видимость Конструкторов

```kotlin
// Private первичный конструктор
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

// Internal конструктор
internal class InternalService internal constructor(val config: Config)

// Protected конструктор (в абстрактном классе)
abstract class BaseRepository protected constructor(val database: Database)
```

### Лучшие Практики

#### ДЕЛАЙТЕ:

```kotlin
// Используйте первичный конструктор с объявлением свойств
class Person(val name: String, val age: Int)

// Используйте значения по умолчанию для необязательных параметров
class Config(val timeout: Int = 5000, val retries: Int = 3)

// Используйте init-блоки для валидации
class Email(val address: String) {
    init {
        require(address.contains("@")) { "Неверный email" }
    }
}

// Используйте именованные аргументы для ясности
val rect = Rectangle(width = 100, height = 50, color = "red")

// Используйте вторичные конструкторы для альтернативных сценариев создания
class User(val id: Int, val name: String) {
    constructor(name: String) : this(name.hashCode(), name)
}
```

#### НЕ ДЕЛАЙТЕ:

```kotlin
// Не дублируйте свойства без необходимости
class Person(name: String, age: Int) {  // Параметры
    val name: String = name              // Лишнее в большинстве случаев
    val age: Int = age                   // Лишнее в большинстве случаев
}
// Лучше: class Person(val name: String, val age: Int)

// Не используйте вторичные конструкторы там, где достаточно значений по умолчанию
class User(val name: String, val age: Int) {
    constructor(name: String) : this(name, 0)  // Плохая практика
}
// Лучше: class User(val name: String, val age: Int = 0)

// Не помещайте тяжелую логику в init-блоки
class Service(val config: Config) {
    init {
        // Избегайте тяжелых вычислений или I/O здесь
        connectToDatabase()  // Плохо: лучше вызвать явно
    }
}

// Не пропускайте валидацию в конструкторах
class Age(val value: Int)  // Плохо: нет валидации
// Лучше:
class Age(val value: Int) {
    init {
        require(value >= 0) { "Возраст не может быть отрицательным" }
    }
}
```

### Общие Паттерны

#### Фабричный Метод С Приватным Конструктором

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

#### Паттерн Builder

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
            require(url.isNotBlank()) { "URL обязателен" }
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

## Answer (EN)

Kotlin has **primary constructors** and **secondary constructors** for initializing class instances. Unlike Java, Kotlin separates constructor parameters from initialization logic, providing a cleaner and more flexible approach to object creation. See also [[c-kotlin]] for more details.

### Key Concepts

1. **Primary Constructor**: Declared in the class header, cannot contain executable code itself (use `init` blocks or property initializers)
2. **Secondary Constructor**: Defined in the class body with the `constructor` keyword
3. **Init Blocks**: Execute initialization code, run together with property initializers as part of the primary constructor in declaration order
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

Init blocks execute initialization code as part of the primary constructor. They are invoked along with property initializers in the order they appear in the class.

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

println(user1)
println(user2)
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
// 1. Primary constructor (parameters)
// 2. Init blocks and property initializers (in declaration order)
// 3. Body of secondary constructor 1
// 4. Body of secondary constructor 2
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
// Don't repeat property declarations without need
class Person(name: String, age: Int) {  // Parameters
    val name: String = name              // Unnecessary in most cases
    val age: Int = age                   // Unnecessary in most cases
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

## Follow-ups

- Compare how constructor overloading in Java maps to Kotlin's primary + secondary constructors and default parameters.
- Explain how `init` blocks interact with property initialization order in more complex class hierarchies.
- Discuss when to prefer factory functions or builder patterns over exposing multiple constructors.

## Дополнительные Вопросы (RU)
- В чем ключевые отличия системы конструкторов Kotlin от Java?
- Когда использовать вторичные конструкторы вместо значений по умолчанию и именованных аргументов?
- Какие распространенные ошибки при использовании `init` и вторичных конструкторов?
## Additional Questions (EN)
- What are the key differences between Kotlin's constructor system and Java's?
- When should you use secondary constructors instead of default values and named arguments?
- What are common pitfalls when using `init` blocks and secondary constructors?
## Ссылки (RU)
- [Kotlin Classes and Inheritance](https://kotlinlang.org/docs/classes.html)
- [Kotlin Constructors](https://kotlinlang.org/docs/classes.html#constructors)
- [Kotlin Properties](https://kotlinlang.org/docs/properties.html)
## References (EN)
- [Kotlin Classes and Inheritance](https://kotlinlang.org/docs/classes.html)
- [Kotlin Constructors](https://kotlinlang.org/docs/classes.html#constructors)
- [Kotlin Properties](https://kotlinlang.org/docs/properties.html)
## Связанные Вопросы (RU)
- [[q-kotlin-init-block--kotlin--easy]]
- [[q-kotlin-properties--kotlin--easy]]
- [[q-kotlin-val-vs-var--kotlin--easy]]
## Related Questions (EN)
- [[q-kotlin-init-block--kotlin--easy]]
- [[q-kotlin-properties--kotlin--easy]]
- [[q-kotlin-val-vs-var--kotlin--easy]]
## MOC Ссылки (RU)
- [[moc-kotlin]]
## MOC Links (EN)
- [[moc-kotlin]]
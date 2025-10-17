---
id: "20251015082237051"
title: "Lazy Initialization / Ленивая инициализация"
topic: kotlin
difficulty: easy
status: draft
created: 2025-10-15
tags: - programming-languages
---
# What function in Kotlin is used for lazy property initialization?

# Question (EN)
> What function in Kotlin is used for lazy property initialization?

# Вопрос (RU)
> Какая функция в Kotlin используется для ленивой инициализации свойства?

---

## Answer (EN)

The `lazy` function is used for lazy property initialization in Kotlin.

**Key characteristics:**
- Property is initialized only when first accessed
- Value is computed and cached on first access
- Thread-safe by default (can be configured)
- Must be used with `val` (read-only property)
- Returns a delegate that implements lazy initialization
- Reduces memory footprint and improves startup performance

**Syntax:**
```kotlin
val propertyName: Type by lazy {
    // Initialization code
    value
}
```

### Code Examples

**Basic lazy initialization:**
```kotlin
class User {
    val name = "Alice"

    // Expensive computation - only calculated when needed
    val profile: String by lazy {
        println("Computing profile...")
        "Profile for $name"
    }
}

fun main() {
    val user = User()
    println("User created")

    // profile is not computed yet
    println("Accessing profile for the first time:")
    println(user.profile)  // Computing profile...
                          // Profile for Alice

    println("Accessing profile again:")
    println(user.profile)  // Profile for Alice (no computation)
}
```

**Lazy initialization with expensive operation:**
```kotlin
class DatabaseConnection {
    val connectionString = "jdbc:mysql://localhost:3306/mydb"

    val connection: String by lazy {
        println("Establishing database connection...")
        Thread.sleep(1000)  // Simulate expensive operation
        println("Connection established!")
        "Connected to $connectionString"
    }
}

fun main() {
    println("Creating database object...")
    val db = DatabaseConnection()

    println("Database object created, but not connected yet")
    println("Doing other work...")

    println("\nNow we need the connection:")
    println(db.connection)  // Connection established now

    println("\nAccessing connection again:")
    println(db.connection)  // No delay, uses cached value
}
```

**Multiple lazy properties:**
```kotlin
class Application {
    val config: Map<String, String> by lazy {
        println("Loading configuration...")
        mapOf(
            "app_name" to "MyApp",
            "version" to "1.0.0",
            "api_url" to "https://api.example.com"
        )
    }

    val logger: String by lazy {
        println("Initializing logger...")
        "Logger for ${config["app_name"]}"
    }

    val cache: MutableMap<String, Any> by lazy {
        println("Creating cache...")
        mutableMapOf<String, Any>()
    }
}

fun main() {
    val app = Application()
    println("Application created\n")

    println("Getting logger:")
    println(app.logger)
    // Loading configuration...
    // Initializing logger...
    // Logger for MyApp

    println("\nGetting cache:")
    println(app.cache)
    // Creating cache...
    // {}
}
```

**Lazy thread safety modes:**
```kotlin
class ThreadSafetyDemo {
    // Default: SYNCHRONIZED (thread-safe)
    val synchronized: String by lazy {
        println("Synchronized initialization")
        "Thread-safe value"
    }

    // PUBLICATION: multiple threads may compute, but only one value is used
    val publication: String by lazy(LazyThreadSafetyMode.PUBLICATION) {
        println("Publication mode initialization")
        "Publication value"
    }

    // NONE: not thread-safe, fastest but only for single-threaded use
    val none: String by lazy(LazyThreadSafetyMode.NONE) {
        println("None mode initialization")
        "Not thread-safe value"
    }
}

fun main() {
    val demo = ThreadSafetyDemo()

    println(demo.synchronized)   // Thread-safe
    println(demo.publication)    // Publication mode
    println(demo.none)           // Not thread-safe
}
```

**Lazy vs lateinit:**
```kotlin
class ComparisonExample {
    // lazy: val, initialized on first access, with initializer
    val lazyProperty: String by lazy {
        "Lazy initialized"
    }

    // lateinit: var, must be initialized before use, no initializer
    lateinit var lateinitProperty: String

    fun initializeLateInit() {
        lateinitProperty = "Late initialized"
    }
}

fun main() {
    val example = ComparisonExample()

    // lazy: can access immediately
    println(example.lazyProperty)  // Lazy initialized

    // lateinit: must initialize first
    example.initializeLateInit()
    println(example.lateinitProperty)  // Late initialized

    // Checking if lateinit is initialized
    if (::lateinitProperty.isInitialized) {
        println("lateinit property is initialized")
    }
}
```

**Real-world example: Lazy loading resources:**
```kotlin
class ImageProcessor {
    private val imagePath = "large_image.png"

    // Heavy object, loaded only when needed
    val imageData: ByteArray by lazy {
        println("Loading image from $imagePath...")
        Thread.sleep(500)  // Simulate file I/O
        ByteArray(1000)  // Simulated image data
    }

    val thumbnail: ByteArray by lazy {
        println("Creating thumbnail from image...")
        imageData.take(100).toByteArray()
    }

    fun getImageSize() = imageData.size

    fun getThumbnailSize() = thumbnail.size
}

fun main() {
    val processor = ImageProcessor()
    println("Image processor created\n")

    // Image not loaded yet
    println("Getting thumbnail:")
    val thumbSize = processor.getThumbnailSize()
    // Loading image from large_image.png...
    // Creating thumbnail from image...
    println("Thumbnail size: $thumbSize\n")

    // Image already loaded
    println("Getting image size:")
    val imgSize = processor.getImageSize()
    println("Image size: $imgSize")
}
```

**Lazy with complex initialization:**
```kotlin
class UserRepository {
    private val users = listOf(
        "Alice" to 30,
        "Bob" to 25,
        "Charlie" to 35
    )

    // Complex computation performed only once
    val statistics: Map<String, Any> by lazy {
        println("Calculating statistics...")

        val averageAge = users.map { it.second }.average()
        val oldestUser = users.maxByOrNull { it.second }
        val youngestUser = users.minByOrNull { it.second }

        mapOf(
            "total_users" to users.size,
            "average_age" to averageAge,
            "oldest" to oldestUser?.first,
            "youngest" to youngestUser?.first
        )
    }

    fun printStats() {
        println("User Statistics:")
        statistics.forEach { (key, value) ->
            println("  $key: $value")
        }
    }
}

fun main() {
    val repo = UserRepository()

    println("Repository created")
    println("Calling printStats():")
    repo.printStats()
    // Calculating statistics...
    // User Statistics:
    //   total_users: 3
    //   average_age: 30.0
    //   oldest: Charlie
    //   youngest: Bob

    println("\nCalling printStats() again:")
    repo.printStats()
    // User Statistics: (no recalculation)
    //   total_users: 3
    //   average_age: 30.0
    //   oldest: Charlie
    //   youngest: Bob
}
```

---

## Ответ (RU)

Функция `lazy` используется для ленивой инициализации свойств в Kotlin.

**Ключевые характеристики:**
- Свойство инициализируется только при первом обращении
- Значение вычисляется и кэшируется при первом доступе
- Потокобезопасна по умолчанию (можно настроить)
- Должна использоваться с `val` (read-only свойством)
- Возвращает делегат, реализующий ленивую инициализацию
- Снижает потребление памяти и улучшает производительность при запуске

**Синтаксис:**
```kotlin
val propertyName: Type by lazy {
    // Код инициализации
    value
}
```

**Пример:**
```kotlin
class User {
    val profile: String by lazy {
        println("Вычисление профиля...")
        "Профиль пользователя"
    }
}

val user = User()
println("Пользователь создан")
// profile ещё не вычислен

println(user.profile)  // Вычисление профиля... Профиль пользователя
println(user.profile)  // Профиль пользователя (без вычисления)
```

**Режимы потокобезопасности:**
- `LazyThreadSafetyMode.SYNCHRONIZED` (по умолчанию) - потокобезопасный
- `LazyThreadSafetyMode.PUBLICATION` - множественное вычисление, но одно значение
- `LazyThreadSafetyMode.NONE` - не потокобезопасный, самый быстрый

**lazy vs lateinit:**
- `lazy`: используется с `val`, инициализация при первом доступе, с инициализатором
- `lateinit`: используется с `var`, должна быть инициализирована до использования, без инициализатора

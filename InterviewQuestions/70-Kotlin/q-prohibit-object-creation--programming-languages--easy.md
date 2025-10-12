---
tags:
  - programming-languages
difficulty: easy
status: draft
---

# How to programmatically prohibit creating a class object?

**English**: How to programmatically prohibit creating a class object in Kotlin?

## Answer (EN)
Make the constructor private to prohibit external object creation. This is used in the Singleton pattern or utility classes (e.g., Math).

**Techniques:**
1. **Private primary constructor** - most common approach
2. **Private secondary constructor** - if primary is not applicable
3. **`object` declaration** - for singletons (no constructor at all)
4. **Abstract class** - cannot be instantiated directly

### Code Examples

**Private primary constructor:**

```kotlin
class Singleton private constructor() {
    companion object {
        private var instance: Singleton? = null

        fun getInstance(): Singleton {
            return instance ?: synchronized(this) {
                instance ?: Singleton().also { instance = it }
            }
        }
    }

    fun doSomething() {
        println("Doing something")
    }
}

fun main() {
    // val singleton = Singleton()  // ERROR: Constructor is private

    // Must use factory method
    val singleton = Singleton.getInstance()
    singleton.doSomething()

    val singleton2 = Singleton.getInstance()
    println(singleton === singleton2)  // true - same instance
}
```

**Utility class with private constructor:**

```kotlin
class MathUtils private constructor() {
    companion object {
        fun add(a: Int, b: Int) = a + b

        fun multiply(a: Int, b: Int) = a * b

        fun factorial(n: Int): Long {
            return if (n <= 1) 1 else n * factorial(n - 1)
        }
    }
}

fun main() {
    // val utils = MathUtils()  // ERROR: Cannot create instance

    // Use static-like methods
    println(MathUtils.add(5, 3))        // 8
    println(MathUtils.multiply(4, 7))   // 28
    println(MathUtils.factorial(5))     // 120
}
```

**Object declaration (better for singletons):**

```kotlin
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

    fun isConnected() = isConnected
}

fun main() {
    // No constructor to call - object is automatically created

    DatabaseConnection.connect()
    println("Connected: ${DatabaseConnection.isConnected()}")

    DatabaseConnection.disconnect()
    println("Connected: ${DatabaseConnection.isConnected()}")
}
```

**Factory pattern with private constructor:**

```kotlin
class User private constructor(
    val id: Int,
    val name: String,
    val email: String
) {
    companion object {
        private var nextId = 1
        private val users = mutableMapOf<Int, User>()

        fun create(name: String, email: String): User {
            val user = User(nextId++, name, email)
            users[user.id] = user
            return user
        }

        fun getById(id: Int): User? = users[id]

        fun getAll(): List<User> = users.values.toList()
    }

    override fun toString() = "User(id=$id, name='$name', email='$email')"
}

fun main() {
    // val user = User(1, "Alice", "alice@example.com")  // ERROR

    // Must use factory method
    val user1 = User.create("Alice", "alice@example.com")
    val user2 = User.create("Bob", "bob@example.com")

    println(user1)
    println(user2)

    println("\nAll users:")
    User.getAll().forEach { println(it) }

    println("\nFind user 1: ${User.getById(1)}")
}
```

**Builder pattern with private constructor:**

```kotlin
class Car private constructor(
    val brand: String,
    val model: String,
    val year: Int,
    val color: String?,
    val sunroof: Boolean
) {
    class Builder {
        private var brand: String = ""
        private var model: String = ""
        private var year: Int = 0
        private var color: String? = null
        private var sunroof: Boolean = false

        fun brand(brand: String) = apply { this.brand = brand }
        fun model(model: String) = apply { this.model = model }
        fun year(year: Int) = apply { this.year = year }
        fun color(color: String) = apply { this.color = color }
        fun sunroof(sunroof: Boolean) = apply { this.sunroof = sunroof }

        fun build(): Car {
            require(brand.isNotBlank()) { "Brand is required" }
            require(model.isNotBlank()) { "Model is required" }
            require(year > 1900) { "Invalid year" }

            return Car(brand, model, year, color, sunroof)
        }
    }

    companion object {
        fun builder() = Builder()
    }

    override fun toString() =
        "Car(brand='$brand', model='$model', year=$year, color=$color, sunroof=$sunroof)"
}

fun main() {
    // val car = Car("Toyota", "Camry", 2023, "Red", false)  // ERROR

    // Must use builder
    val car = Car.builder()
        .brand("Toyota")
        .model("Camry")
        .year(2023)
        .color("Red")
        .sunroof(true)
        .build()

    println(car)
}
```

**Private constructor with validation:**

```kotlin
class Email private constructor(val address: String) {
    companion object {
        fun create(address: String): Email? {
            return if (isValid(address)) {
                Email(address)
            } else {
                null
            }
        }

        fun createOrThrow(address: String): Email {
            require(isValid(address)) { "Invalid email: $address" }
            return Email(address)
        }

        private fun isValid(address: String): Boolean {
            return address.contains("@") &&
                    address.contains(".") &&
                    address.length >= 5
        }
    }

    override fun toString() = "Email($address)"
}

fun main() {
    // val email = Email("test@example.com")  // ERROR

    // Must use factory methods
    val validEmail = Email.create("user@example.com")
    println(validEmail)  // Email(user@example.com)

    val invalidEmail = Email.create("invalid")
    println(invalidEmail)  // null

    try {
        Email.createOrThrow("bad-email")
    } catch (e: IllegalArgumentException) {
        println("Error: ${e.message}")
    }
}
```

**Abstract class (cannot instantiate):**

```kotlin
abstract class Shape {
    abstract val area: Double
    abstract val perimeter: Double

    fun describe() {
        println("Area: $area, Perimeter: $perimeter")
    }
}

class Circle(val radius: Double) : Shape() {
    override val area: Double
        get() = Math.PI * radius * radius

    override val perimeter: Double
        get() = 2 * Math.PI * radius
}

class Rectangle(val width: Double, val height: Double) : Shape() {
    override val area: Double
        get() = width * height

    override val perimeter: Double
        get() = 2 * (width + height)
}

fun main() {
    // val shape = Shape()  // ERROR: Cannot instantiate abstract class

    val circle = Circle(5.0)
    circle.describe()

    val rectangle = Rectangle(10.0, 5.0)
    rectangle.describe()
}
```

**Sealed class (cannot instantiate directly):**

```kotlin
sealed class Result {
    data class Success(val value: Int) : Result()
    data class Error(val message: String) : Result()
}

fun main() {
    // val result = Result()  // ERROR: Cannot instantiate sealed class

    // Can only create subclasses
    val success = Result.Success(42)
    val error = Result.Error("Something went wrong")

    println(success)
    println(error)
}
```

**Private init block:**

```kotlin
class RestrictedClass {
    init {
        throw UnsupportedOperationException("Cannot create instance directly")
    }

    companion object {
        fun createSpecial(): RestrictedClass {
            // This won't work either due to init block
            // return RestrictedClass()
        }
    }
}

// Better approach: private constructor
class BetterRestrictedClass private constructor() {
    companion object {
        fun createSpecial(): BetterRestrictedClass {
            return BetterRestrictedClass()
        }
    }
}

fun main() {
    // val obj = RestrictedClass()  // Would throw exception

    val obj = BetterRestrictedClass.createSpecial()
    println("Created: $obj")
}
```

**Configuration class with private constructor:**

```kotlin
class AppConfig private constructor(
    val apiUrl: String,
    val timeout: Int,
    val debugMode: Boolean
) {
    companion object {
        private var instance: AppConfig? = null

        fun initialize(
            apiUrl: String,
            timeout: Int = 30,
            debugMode: Boolean = false
        ) {
            require(instance == null) { "Config already initialized" }
            instance = AppConfig(apiUrl, timeout, debugMode)
        }

        fun getInstance(): AppConfig {
            return instance ?: error("Config not initialized")
        }
    }

    override fun toString() =
        "AppConfig(apiUrl='$apiUrl', timeout=$timeout, debugMode=$debugMode)"
}

fun main() {
    // val config = AppConfig("url", 30, false)  // ERROR

    // Must initialize first
    AppConfig.initialize(
        apiUrl = "https://api.example.com",
        timeout = 60,
        debugMode = true
    )

    val config = AppConfig.getInstance()
    println(config)

    // Cannot initialize again
    try {
        AppConfig.initialize("another-url")
    } catch (e: IllegalArgumentException) {
        println("Error: ${e.message}")
    }
}
```

---

## Ответ (RU)
# Вопрос (RU)
Как программно запретить создание объекта класса

## Ответ (RU)
Сделать приватный конструктор, чтобы запретить внешнее создание объекта. Используется в паттерне Singleton или Utility-классах например Math

---
id: kotlin-224
title: "Prohibit Object Creation / Запрет создания объектов"
aliases: [Private Constructor, Prohibit Creation, Utility Classes, Запрет создания]
topic: kotlin
subtopics: [classes, design]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-sequences-vs-collections-performance--kotlin--medium, q-structured-concurrency-violations--kotlin--hard]
created: 2025-10-15
updated: 2025-11-10
tags: [classes, constructor, design, difficulty/easy, kotlin, singleton]
---
# Вопрос (RU)

> Как программно запретить создание объекта (экземпляра) класса в Kotlin?

# Question (EN)

> How to programmatically prohibit creating a class object in Kotlin?

## Ответ (RU)

Чтобы программно запретить создание экземпляров класса извне в Kotlin, используют:

- Приватный конструктор (primary или secondary) плюс фабричные методы.
- `object`-декларацию для синглтонов (конструктора нет, экземпляр управляется языком).

Другие подходы (abstract/sealed классы) ограничивают создание экземпляров, но в первую очередь служат для моделирования и не являются базовым ответом на этот вопрос.

**Основные подходы:**
1. **Приватный primary constructor** – запрещаем прямое создание и открываем только контролируемые фабрики.
2. **Приватный secondary constructor** – если нужно ограничить отдельные пути создания.
3. **`object` declaration** – предпочтительный способ реализации синглтонов.
4. **Utility-класс с приватным конструктором** – чтобы нельзя было создать экземпляр, но в Kotlin обычно лучше использовать top-level функции или `object`.

### Примеры Кода

**Приватный primary constructor с фабрикой (ручной singleton-стиль):**

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
    // val singleton = Singleton()  // ОШИБКА: конструктор приватный

    val singleton = Singleton.getInstance()
    singleton.doSomething()

    val singleton2 = Singleton.getInstance()
    println(singleton === singleton2)  // true - тот же экземпляр
}
```

Примечание: в Kotlin для синглтонов обычно следует использовать `object`, а не ручную реализацию, если нет особых требований к ленивой инициализации.

**Utility-класс с приватным конструктором:**

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
    // val utils = MathUtils()  // ОШИБКА: нельзя создать экземпляр

    println(MathUtils.add(5, 3))        // 8
    println(MathUtils.multiply(4, 7))   // 28
    println(MathUtils.factorial(5))     // 120
}
```

Примечание: в Kotlin вместо Java-стиля utility-классов лучше использовать top-level функции или `object`.

**Object declaration (предпочтительно для синглтонов):**

```kotlin
object DatabaseConnection {
    private var isConnected = false

    fun connect() {
        if (!isConnected) {
            println("Подключение к БД...")
            isConnected = true
        }
    }

    fun disconnect() {
        if (isConnected) {
            println("Отключение от БД...")
            isConnected = false
        }
    }

    fun isConnected() = isConnected
}

fun main() {
    // Нет конструктора для вызова — экземпляр управляется Kotlin

    DatabaseConnection.connect()
    println("Подключен: ${DatabaseConnection.isConnected()}")

    DatabaseConnection.disconnect()
    println("Подключен: ${DatabaseConnection.isConnected()}")
}
```

**Factory pattern с приватным конструктором:**

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
    // val user = User(1, "Alice", "alice@example.com")  // ОШИБКА: конструктор приватный

    val user1 = User.create("Alice", "alice@example.com")
    val user2 = User.create("Bob", "bob@example.com")

    println(user1)
    println(user2)

    println("\nВсе пользователи:")
    User.getAll().forEach { println(it) }

    println("\nПользователь с id=1: ${User.getById(1)}")
}
```

**Builder pattern с приватным конструктором:**

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
            require(brand.isNotBlank()) { "Бренд обязателен" }
            require(model.isNotBlank()) { "Модель обязательна" }
            require(year > 1900) { "Неверный год" }

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
    // val car = Car("Toyota", "Camry", 2023, "Red", false)  // ОШИБКА: конструктор приватный

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

**Приватный конструктор с валидацией (value object):**

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
    // val email = Email("test@example.com")  // ОШИБКА: конструктор приватный

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

**Abstract class (нельзя создать напрямую):**

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
    // val shape = Shape()  // ОШИБКА: нельзя создать abstract-класс

    val circle = Circle(5.0)
    circle.describe()

    val rectangle = Rectangle(10.0, 5.0)
    rectangle.describe()
}
```

**Sealed class (нельзя создать напрямую):**

```kotlin
sealed class Result {
    data class Success(val value: Int) : Result()
    data class Error(val message: String) : Result()
}

fun main() {
    // val result = Result()  // ОШИБКА: нельзя создать sealed-класс напрямую

    val success = Result.Success(42)
    val error = Result.Error("Что-то пошло не так")

    println(success)
    println(error)
}
```

Примечание: abstract и sealed классы ограничивают создание экземпляров по смысловым причинам; не стоит использовать их только как искусственный запрет, если достаточно приватного конструктора или `object`.

**Не стоит эмулировать запрет через init-блок:**

```kotlin
class RestrictedClass {
    init {
        throw UnsupportedOperationException("Cannot create instance directly")
    }
}
```

Формально это блокирует успешное создание, но делает это через runtime-исключение, а не через модель типов. Предпочтительнее приватный конструктор или `object`:

```kotlin
class BetterRestrictedClass private constructor() {
    companion object {
        fun createSpecial(): BetterRestrictedClass {
            return BetterRestrictedClass()
        }
    }
}

fun main() {
    // val obj = BetterRestrictedClass()  // ОШИБКА: конструктор приватный

    val obj = BetterRestrictedClass.createSpecial()
    println("Создано: $obj")
}
```

**Configuration-класс с приватным конструктором:**

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
    // val config = AppConfig("url", 30, false)  // ОШИБКА: конструктор приватный

    AppConfig.initialize(
        apiUrl = "https://api.example.com",
        timeout = 60,
        debugMode = true
    )

    val config = AppConfig.getInstance()
    println(config)

    try {
        AppConfig.initialize("another-url")
    } catch (e: IllegalArgumentException) {
        println("Error: ${e.message}")
    }
}
```

## Answer (EN)

The idiomatic ways to prohibit external creation of class instances in Kotlin are:

- Use a private constructor (primary or secondary) and expose only factory methods.
- Use an `object` declaration for singletons (no public constructor).

Other types like abstract or sealed classes cannot be instantiated directly, but they are modeling tools first, and should not be the primary answer to this question.

**Techniques:**
1. **Private primary constructor** – prevent direct instantiation and expose factories.
2. **Private secondary constructor** – when a non-private primary exists but some construction paths must be restricted.
3. **`object` declaration** – preferred for singletons; instance is created by the language, no `new`/constructor.
4. **Utility holder with private constructor** – to prevent instantiation when using companion/top-level-style utilities (though top-level functions or `object` are usually better in Kotlin).

### Code Examples

**Private primary constructor with factory (manual singleton-style access):**

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

Note: In Kotlin, prefer `object` declarations for singletons (see below) instead of manual patterns like this unless you specifically need lazy init with custom semantics.

**Utility class with private constructor (to prevent instantiation):**

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

    println(MathUtils.add(5, 3))        // 8
    println(MathUtils.multiply(4, 7))   // 28
    println(MathUtils.factorial(5))     // 120
}
```

Note: In Kotlin, prefer top-level functions or an `object` rather than a Java-style utility class.

**Object declaration (preferred for singletons):**

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
    // No constructor to call - object instance is managed by Kotlin

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
    // val user = User(1, "Alice", "alice@example.com")  // ERROR: Constructor is private

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
    // val car = Car("Toyota", "Camry", 2023, "Red", false)  // ERROR: Constructor is private

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

**Private constructor with validation (value object):**

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
    // val email = Email("test@example.com")  // ERROR: Constructor is private

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

**Abstract class (cannot instantiate directly):**

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

    val success = Result.Success(42)
    val error = Result.Error("Something went wrong")

    println(success)
    println(error)
}
```

Note: Abstract and sealed classes limit direct instantiation by design, but they are chosen for type modeling; don't use them solely to "ban" object creation when a private constructor or `object` suffices.

**Avoid using init blocks to simulate prohibition:**

```kotlin
class RestrictedClass {
    init {
        throw UnsupportedOperationException("Cannot create instance directly")
    }
}
```

This technically prevents successful instantiation, but it's non-idiomatic and throws at runtime instead of expressing the constraint in the type system. Prefer a `private constructor` or `object`:

```kotlin
class BetterRestrictedClass private constructor() {
    companion object {
        fun createSpecial(): BetterRestrictedClass {
            return BetterRestrictedClass()
        }
    }
}

fun main() {
    // val obj = BetterRestrictedClass()  // ERROR: Constructor is private

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
    // val config = AppConfig("url", 30, false)  // ERROR: Constructor is private

    AppConfig.initialize(
        apiUrl = "https://api.example.com",
        timeout = 60,
        debugMode = true
    )

    val config = AppConfig.getInstance()
    println(config)

    try {
        AppConfig.initialize("another-url")
    } catch (e: IllegalArgumentException) {
        println("Error: ${e.message}")
    }
}
```

## Follow-ups

- What are the key differences between this and Java?
- When would you use each of these approaches in practice?
- What are common pitfalls to avoid (e.g., overusing utility classes instead of top-level functions/objects)?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Related Questions

- [[q-structured-concurrency-violations--kotlin--hard]]
- [[q-sequences-vs-collections-performance--kotlin--medium]]

---
id: "20251015082236013"
title: "Property Delegates / Делегаты свойств"
topic: kotlin
difficulty: medium
status: draft
created: 2025-10-15
tags: - kotlin
  - delegates
  - properties
---
# В чем особенность делегатов свойств

**English**: What is special about property delegates in Kotlin?

## Answer (EN)
Делегаты свойств (Property Delegates) — это мощная функциональность Kotlin, позволяющая делегировать выполнение операций получения и установки значения свойства другому объекту.

### Main idea

Instead of each property storing data or performing operations independently, it can delegate these tasks to another object.

```kotlin
class Example {
    // Normal property
    var normalProperty: String = ""

    // Delegated property
    var delegatedProperty: String by Delegate()
}
```

### Standard delegates

#### 1. lazy - lazy initialization

Value is computed only on first access.

```kotlin
class DatabaseConnection {
    // Initialized only on first use
    val database: Database by lazy {
        println("Initializing database...")
        Database.connect("jdbc:mysql://localhost/mydb")
    }

    fun query() {
        database.execute("SELECT * FROM users")  // Initialization happens here
    }
}

// Usage example
val connection = DatabaseConnection()
// "Initializing database..." not printed yet
connection.query()  // Now prints "Initializing database..."
connection.query()  // Database already initialized, not created again
```

#### 2. observable - change observation

```kotlin
class User {
    var name: String by Delegates.observable("Initial Name") { property, oldValue, newValue ->
        println("${property.name} changed from $oldValue to $newValue")
    }
}

// Usage
val user = User()
user.name = "Alice"  // Prints: name changed from Initial Name to Alice
user.name = "Bob"    // Prints: name changed from Alice to Bob
```

#### 3. vetoable - validation before change

```kotlin
class Product {
    var price: Int by Delegates.vetoable(0) { _, oldValue, newValue ->
        newValue >= 0  // Allow change only if new price >= 0
    }
}

// Usage
val product = Product()
product.price = 100   // OK, price set
product.price = -50   // Rejected, price remains 100
println(product.price)  // 100
```

#### 4. notNull - late initialization with check

```kotlin
class Configuration {
    var apiKey: String by Delegates.notNull()

    fun initialize() {
        apiKey = "your_api_key"  // Must be set before first read
    }

    fun makeRequest() {
        println("Using API key: $apiKey")  // IllegalStateException if not initialized
    }
}
```

### Custom delegates

```kotlin
// Delegate for logging property access
class LoggingDelegate<T>(private var value: T) : ReadWriteProperty<Any?, T> {
    override fun getValue(thisRef: Any?, property: KProperty<*>): T {
        println("Getting ${property.name} = $value")
        return value
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        println("Setting ${property.name} from ${this.value} to $value")
        this.value = value
    }
}

// Usage
class Example {
    var data: String by LoggingDelegate("initial")
}

val example = Example()
example.data  // Getting data = initial
example.data = "new value"  // Setting data from initial to new value
```

### Delegate for SharedPreferences

```kotlin
class SharedPreferencesDelegate<T>(
    private val prefs: SharedPreferences,
    private val key: String,
    private val defaultValue: T
) : ReadWriteProperty<Any?, T> {

    @Suppress("UNCHECKED_CAST")
    override fun getValue(thisRef: Any?, property: KProperty<*>): T {
        return when (defaultValue) {
            is Boolean -> prefs.getBoolean(key, defaultValue) as T
            is Int -> prefs.getInt(key, defaultValue) as T
            is Long -> prefs.getLong(key, defaultValue) as T
            is Float -> prefs.getFloat(key, defaultValue) as T
            is String -> prefs.getString(key, defaultValue) as T
            else -> throw IllegalArgumentException("Unsupported type")
        }
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        prefs.edit {
            when (value) {
                is Boolean -> putBoolean(key, value)
                is Int -> putInt(key, value)
                is Long -> putLong(key, value)
                is Float -> putFloat(key, value)
                is String -> putString(key, value)
            }
        }
    }
}

// Extension function for convenience
fun <T> SharedPreferences.delegate(key: String, defaultValue: T) =
    SharedPreferencesDelegate(this, key, defaultValue)

// Usage
class Settings(context: Context) {
    private val prefs = context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE)

    var username: String by prefs.delegate("username", "")
    var age: Int by prefs.delegate("age", 0)
    var isFirstLaunch: Boolean by prefs.delegate("first_launch", true)
}

val settings = Settings(context)
settings.username = "Alice"  // Automatically saved to SharedPreferences
println(settings.username)   // Automatically read from SharedPreferences
```

### Map delegates

```kotlin
class User(map: Map<String, Any?>) {
    val name: String by map
    val age: Int by map
    val email: String by map
}

// Usage
val userMap = mapOf(
    "name" to "Alice",
    "age" to 30,
    "email" to "alice@example.com"
)

val user = User(userMap)
println(user.name)   // Alice
println(user.age)    // 30
```

### Key features and benefits

#### 1. Logic isolation

Getter/setter logic is extracted into a separate class.

```kotlin
class ValidationDelegate(private var value: String) : ReadWriteProperty<Any?, String> {
    override fun getValue(thisRef: Any?, property: KProperty<*>) = value

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: String) {
        require(value.isNotBlank()) { "Value cannot be blank" }
        require(value.length <= 100) { "Value too long" }
        this.value = value
    }
}

class Form {
    var email: String by ValidationDelegate("")
    var username: String by ValidationDelegate("")
}
```

#### 2. Code reusability

One delegate can be used for multiple properties.

```kotlin
class RangeDelegate(private var value: Int, private val range: IntRange) :
    ReadWriteProperty<Any?, Int> {

    override fun getValue(thisRef: Any?, property: KProperty<*>) = value

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: Int) {
        require(value in range) { "$value is not in range $range" }
        this.value = value
    }
}

class GameCharacter {
    var health: Int by RangeDelegate(100, 0..100)
    var mana: Int by RangeDelegate(50, 0..100)
    var stamina: Int by RangeDelegate(75, 0..100)
}
```

#### 3. Extensibility

Easy to create new delegates for specific needs.

#### 4. Built-in language support

Kotlin provides `by` syntax for working with delegates.

**English**: Property delegates allow delegating getter/setter operations to another object, avoiding code duplication and making code modular. Built-in delegates include `lazy` (lazy initialization), `observable` (change observation), `vetoable` (validation), and `notNull`. Custom delegates implement `ReadWriteProperty` interface, enabling reusable logic for SharedPreferences, validation, logging, etc.

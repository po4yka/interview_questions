---
id: kotlin-147
title: "Property Delegates / Делегаты свойств"
aliases: [Delegates, Property, Property Delegates, Делегаты свойств]
topic: kotlin
subtopics: [delegates]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-coroutine-memory-leak-detection--kotlin--hard, q-dispatchers-unconfined--kotlin--medium, q-stateflow-sharedflow-differences--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [delegates, difficulty/medium, kotlin, properties]
date created: Friday, October 31st 2025, 6:30:28 pm
date modified: Saturday, November 1st 2025, 5:43:24 pm
---

# В Чем Особенность Делегатов Свойств

**English**: What is special about property delegates in Kotlin?

## Answer (EN)
Делегаты свойств (Property Delegates) — это мощная функциональность Kotlin, позволяющая делегировать выполнение операций получения и установки значения свойства другому объекту.

### Main Idea

Instead of each property storing data or performing operations independently, it can delegate these tasks to another object.

```kotlin
class Example {
    // Normal property
    var normalProperty: String = ""

    // Delegated property
    var delegatedProperty: String by Delegate()
}
```

### Standard Delegates

#### 1. Lazy - Lazy Initialization

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

#### 2. Observable - Change Observation

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

#### 3. Vetoable - Validation before Change

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

#### 4. notNull - Late Initialization with Check

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

### Custom Delegates

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

### Map Delegates

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

### Key Features and Benefits

#### 1. Logic Isolation

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

#### 2. Code Reusability

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

#### 4. Built-in Language Support

Kotlin provides `by` syntax for working with delegates.

**English**: Property delegates allow delegating getter/setter operations to another object, avoiding code duplication and making code modular. Built-in delegates include `lazy` (lazy initialization), `observable` (change observation), `vetoable` (validation), and `notNull`. Custom delegates implement `ReadWriteProperty` interface, enabling reusable logic for SharedPreferences, validation, logging, etc.

## Ответ (RU)

Делегаты свойств (Property Delegates) позволяют делегировать операции получения и установки значения свойства другому объекту, избегая дублирования кода и делая код модульным.

### Встроенные Делегаты

- **lazy** - ленивая инициализация (значение вычисляется только при первом обращении)
- **observable** - наблюдение за изменениями (вызывается callback при каждом изменении)
- **vetoable** - валидация перед изменением (можно отклонить новое значение)
- **notNull** - поздняя инициализация с проверкой (IllegalStateException если не инициализировано)

### Пользовательские Делегаты

Реализуют интерфейс `ReadWriteProperty`, что позволяет создавать переиспользуемую логику для:
- SharedPreferences (автоматическое сохранение/чтение)
- Валидация (проверка значений перед установкой)
- Логирование (запись всех изменений)
- Кеширование и другие задачи

Пользовательские делегаты позволяют вынести сложную логику getter/setter в отдельный класс и переиспользовать её для нескольких свойств.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-coroutine-memory-leak-detection--kotlin--hard]]
- [[q-dispatchers-unconfined--kotlin--medium]]
- [[q-stateflow-sharedflow-differences--kotlin--medium]]

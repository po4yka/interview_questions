---
id: kotlin-203
title: "Interface Properties / Свойства интерфейсов"
aliases: []
topic: kotlin
subtopics: [access-modifiers, null-safety, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-inline-functions--kotlin--medium, q-kotlin-delegation-detailed--kotlin--medium, q-statein-sharein-flow--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/medium]
date created: Sunday, October 12th 2025, 3:43:42 pm
date modified: Saturday, November 1st 2025, 5:43:22 pm
---

# How to Operate with Properties in Interface?

# Question (EN)
> How to operate with properties in interfaces in Kotlin?

# Вопрос (RU)
> Как работать со свойствами в интерфейсах в Kotlin?

---

## Answer (EN)

In an interface, you can declare `val` or `var` properties without initialization. For properties with `get`, the implementation can be in the interface through a custom getter. For `var` with `set`, the implementation must be in the class, as interfaces do not have state and cannot use backing fields (`field`).

**Key rules:**
- Interface properties cannot have backing fields
- Can have custom getters in the interface
- `var` properties can declare setters, but need implementation in class
- Properties can be abstract (no implementation) or have default implementation
- Can override properties in implementing classes

### Code Examples

**Basic interface properties:**

```kotlin
interface User {
    // Abstract property - must be implemented
    val name: String

    // Abstract property with type
    val email: String

    // Property with custom getter - has implementation
    val displayName: String
        get() = "User: $name"

    // Property with custom getter using other properties
    val isValid: Boolean
        get() = name.isNotEmpty() && email.contains("@")
}

class BasicUser(
    override val name: String,
    override val email: String
) : User

fun main() {
    val user = BasicUser("Alice", "alice@example.com")

    println("Name: ${user.name}")
    println("Email: ${user.email}")
    println("Display name: ${user.displayName}")  // User: Alice
    println("Is valid: ${user.isValid}")  // true
}
```

**val vs var in interfaces:**

```kotlin
interface Config {
    // val - read-only, can have getter
    val apiUrl: String
        get() = "https://api.example.com"  // Default implementation

    // var - can be overridden as read-write
    var timeout: Int

    // var with custom getter
    var debugMode: Boolean
        get() = false  // Default value
}

class AppConfig : Config {
    // Can override val with val
    override val apiUrl: String = "https://api.production.com"

    // Must provide backing field for var
    override var timeout: Int = 30

    // Can override with backing field
    override var debugMode: Boolean = false
}

fun main() {
    val config = AppConfig()

    println("API URL: ${config.apiUrl}")
    println("Timeout: ${config.timeout}")

    // Can modify var properties
    config.timeout = 60
    config.debugMode = true

    println("New timeout: ${config.timeout}")
    println("Debug mode: ${config.debugMode}")
}
```

**Custom getters in interface:**

```kotlin
interface Shape {
    val width: Double
    val height: Double

    // Computed property with getter
    val area: Double
        get() = width * height

    val perimeter: Double
        get() = 2 * (width + height)

    val diagonal: Double
        get() = Math.sqrt(width * width + height * height)
}

class Rectangle(
    override val width: Double,
    override val height: Double
) : Shape

fun main() {
    val rect = Rectangle(10.0, 5.0)

    println("Width: ${rect.width}")
    println("Height: ${rect.height}")
    println("Area: ${rect.area}")         // 50.0
    println("Perimeter: ${rect.perimeter}") // 30.0
    println("Diagonal: ${rect.diagonal}")   // 11.18...
}
```

**Properties with setter (must be implemented in class):**

```kotlin
interface Nameable {
    var name: String

    // Can have custom getter
    val upperCaseName: String
        get() = name.uppercase()
}

class Person(override var name: String) : Nameable {
    // name has both getter and setter from property
}

class Product : Nameable {
    // Custom implementation with backing field
    private var _name: String = ""

    override var name: String
        get() = _name
        set(value) {
            require(value.isNotBlank()) { "Name cannot be blank" }
            _name = value.trim()
        }
}

fun main() {
    val person = Person("alice")
    println("Person: ${person.name}")
    println("Upper: ${person.upperCaseName}")

    person.name = "bob"
    println("Updated: ${person.name}")

    val product = Product()
    product.name = "  Laptop  "
    println("Product: '${product.name}'")  // 'Laptop' (trimmed)
    println("Upper: ${product.upperCaseName}")

    // This would throw exception:
    // product.name = "  "
}
```

**Multiple interface properties:**

```kotlin
interface Identifiable {
    val id: String
}

interface Timestamped {
    val createdAt: Long
    val updatedAt: Long

    val age: Long
        get() = System.currentTimeMillis() - createdAt
}

interface Nameable {
    val name: String
    val displayName: String
        get() = name
}

data class Article(
    override val id: String,
    override val name: String,
    override val createdAt: Long,
    override val updatedAt: Long
) : Identifiable, Timestamped, Nameable {
    override val displayName: String
        get() = "Article: $name"
}

fun main() {
    val article = Article(
        id = "article-001",
        name = "Kotlin Basics",
        createdAt = System.currentTimeMillis() - 1000000,
        updatedAt = System.currentTimeMillis()
    )

    println("ID: ${article.id}")
    println("Name: ${article.name}")
    println("Display: ${article.displayName}")
    println("Age: ${article.age} ms")
}
```

**Overriding interface properties:**

```kotlin
interface Animal {
    val species: String
    val sound: String
        get() = "Generic sound"
}

class Dog : Animal {
    override val species: String = "Canis familiaris"

    // Override with custom getter
    override val sound: String
        get() = "Woof!"
}

class Cat : Animal {
    override val species: String = "Felis catus"

    // Override with backing field
    override val sound: String = "Meow!"
}

fun main() {
    val dog = Dog()
    val cat = Cat()

    println("Dog species: ${dog.species}, sound: ${dog.sound}")
    println("Cat species: ${cat.species}, sound: ${cat.sound}")
}
```

**Properties with delegation:**

```kotlin
interface DataProvider {
    val data: List<String>
    val size: Int
        get() = data.size

    val isEmpty: Boolean
        get() = data.isEmpty()

    val firstOrNull: String?
        get() = data.firstOrNull()
}

class StringListProvider(override val data: List<String>) : DataProvider

class LazyDataProvider : DataProvider {
    override val data: List<String> by lazy {
        println("Loading data...")
        listOf("Item 1", "Item 2", "Item 3")
    }
}

fun main() {
    val provider1 = StringListProvider(listOf("A", "B", "C"))
    println("Provider 1 size: ${provider1.size}")
    println("Provider 1 first: ${provider1.firstOrNull}")

    val provider2 = LazyDataProvider()
    println("Provider 2 created (data not loaded yet)")
    println("Provider 2 size: ${provider2.size}")  // Data loaded here
    println("Provider 2 first: ${provider2.firstOrNull}")
}
```

**const in companion object of interface:**

```kotlin
interface Constants {
    companion object {
        const val MAX_SIZE = 100
        const val DEFAULT_TIMEOUT = 30
        const val API_VERSION = "v1"
    }

    val maxRetries: Int
        get() = 3
}

class Service : Constants {
    fun performAction() {
        println("Max size: ${Constants.MAX_SIZE}")
        println("Max retries: $maxRetries")
    }
}

fun main() {
    println("API Version: ${Constants.API_VERSION}")

    val service = Service()
    service.performAction()
}
```

**Complex example with validation:**

```kotlin
interface Validatable {
    val isValid: Boolean
        get() = validate().isEmpty()

    fun validate(): List<String>
}

interface UserData : Validatable {
    val username: String
    val email: String
    val age: Int

    override fun validate(): List<String> {
        val errors = mutableListOf<String>()

        if (username.length < 3) {
            errors.add("Username must be at least 3 characters")
        }

        if (!email.contains("@")) {
            errors.add("Invalid email format")
        }

        if (age < 0 || age > 150) {
            errors.add("Age must be between 0 and 150")
        }

        return errors
    }
}

data class User(
    override val username: String,
    override val email: String,
    override val age: Int
) : UserData

fun main() {
    val validUser = User("alice", "alice@example.com", 30)
    println("Valid user: ${validUser.isValid}")
    println("Errors: ${validUser.validate()}")

    val invalidUser = User("al", "invalid-email", -5)
    println("\nInvalid user: ${invalidUser.isValid}")
    println("Errors:")
    invalidUser.validate().forEach { println("  - $it") }
}
```

**No backing field in interface:**

```kotlin
interface Counter {
    // This would NOT compile in interface:
    // var count: Int = 0  // Error: Property initializers are not allowed in interfaces

    // This would NOT compile:
    // var count: Int
    //     get() = field  // Error: 'field' is not available in interface
    //     set(value) { field = value }

    // This WORKS - no backing field needed:
    var currentValue: Int
        get() = getCurrentCount()
        set(value) = setCurrentCount(value)

    fun getCurrentCount(): Int
    fun setCurrentCount(value: Int)
}

class CounterImpl : Counter {
    private var count = 0

    override fun getCurrentCount() = count

    override fun setCurrentCount(value: Int) {
        count = value
    }
}

fun main() {
    val counter = CounterImpl()
    println("Current: ${counter.currentValue}")

    counter.currentValue = 10
    println("Updated: ${counter.currentValue}")
}
```

---

## Ответ (RU)

В интерфейсе можно объявить `val` или `var` свойства без инициализации. Для свойств с `get` реализация может быть в интерфейсе через кастомный геттер. Для `var` с `set` реализация должна быть в классе, так как интерфейсы не имеют состояния и не могут использовать backing fields (`field`).

**Ключевые правила:**
- Свойства интерфейса не могут иметь backing fields
- Могут иметь кастомные геттеры в интерфейсе
- Свойства `var` могут объявлять сеттеры, но нуждаются в реализации в классе
- Свойства могут быть абстрактными (без реализации) или иметь реализацию по умолчанию
- Можно переопределять свойства в реализующих классах

## Related Questions

- [[q-statein-sharein-flow--kotlin--medium]]
- [[q-inline-functions--kotlin--medium]]
- [[q-kotlin-delegation-detailed--kotlin--medium]]

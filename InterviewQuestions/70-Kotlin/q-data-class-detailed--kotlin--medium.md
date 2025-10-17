---
id: "20251012-150011"
title: "Data classes in Kotlin: features, limitations, and best practices"
topic: kotlin
difficulty: medium
status: draft
created: "2025-10-12"
tags: ["kotlin", "classes", "data-class", "kotlin-features", "difficulty/medium"]
description: "Comprehensive guide to Kotlin data classes covering generated methods, copy(), componentN(), destructuring, limitations, and when to use them"
moc: "moc-kotlin"
subtopics: ["classes", "data-class", "kotlin-features"]
---
# Data classes in Kotlin: features, limitations, and best practices

## English

### Problem Statement

Data classes are one of Kotlin's most powerful features for representing data. They automatically generate useful methods and support destructuring, but they also have limitations. What methods are generated, when should data classes be used, and what are their constraints?

### Solution

A **data class** in Kotlin is a class whose primary purpose is to hold data. The compiler automatically generates `equals()`, `hashCode()`, `toString()`, `copy()`, and `componentN()` functions.

#### Basic Data Class

```kotlin
// Simple data class
data class User(
    val id: String,
    val name: String,
    val email: String
)

fun basicUsage() {
    val user = User("1", "John Doe", "john@example.com")

    // Auto-generated toString()
    println(user) // User(id=1, name=John Doe, email=john@example.com)

    // Auto-generated equals()
    val user2 = User("1", "John Doe", "john@example.com")
    println(user == user2) // true

    // Auto-generated hashCode()
    println(user.hashCode() == user2.hashCode()) // true

    // Auto-generated copy()
    val user3 = user.copy(name = "Jane Doe")
    println(user3) // User(id=1, name=Jane Doe, email=john@example.com)
}
```

#### Generated Functions

```kotlin
data class Person(val name: String, val age: Int)

fun demonstrateGeneratedFunctions() {
    val person = Person("Alice", 30)

    // 1. toString()
    val stringRepresentation = person.toString()
    println(stringRepresentation) // Person(name=Alice, age=30)

    // 2. equals()
    val person2 = Person("Alice", 30)
    val person3 = Person("Bob", 25)
    println(person == person2) // true (structural equality)
    println(person == person3) // false

    // 3. hashCode()
    println(person.hashCode()) // Consistent with equals()
    val set = setOf(person, person2)
    println(set.size) // 1 (person and person2 are equal)

    // 4. copy()
    val olderPerson = person.copy(age = 31)
    println(olderPerson) // Person(name=Alice, age=31)

    // 5. componentN() - for destructuring
    val (name, age) = person
    println("Name: $name, Age: $age") // Name: Alice, Age: 30
}
```

#### Copy Function

```kotlin
data class Product(
    val id: String,
    val name: String,
    val price: Double,
    val inStock: Boolean = true
)

fun copyin Examples() {
    val product = Product("1", "Laptop", 999.99, true)

    // Copy with single property change
    val updatedPrice = product.copy(price = 899.99)

    // Copy with multiple property changes
    val outOfStock = product.copy(
        price = 799.99,
        inStock = false
    )

    // Copy with default parameter
    val newProduct = product.copy(
        id = "2",
        name = "Desktop"
        // price and inStock keep original values
    )

    // Immutability pattern
    class ProductRepository {
        private val products = mutableListOf<Product>()

        fun updatePrice(id: String, newPrice: Double) {
            val index = products.indexOfFirst { it.id == id }
            if (index != -1) {
                products[index] = products[index].copy(price = newPrice)
            }
        }
    }
}
```

#### Destructuring Declarations

```kotlin
data class Coordinate(val x: Double, val y: Double, val z: Double)

fun destructuringExamples() {
    val point = Coordinate(1.0, 2.0, 3.0)

    // Destructure all properties
    val (x, y, z) = point
    println("x=$x, y=$y, z=$z")

    // Destructure partially (use _ for unused)
    val (x2, _, z2) = point
    println("x=$x2, z=$z2")

    // In lambda parameters
    val points = listOf(
        Coordinate(1.0, 2.0, 3.0),
        Coordinate(4.0, 5.0, 6.0)
    )

    points.forEach { (x, y, z) ->
        println("Point: ($x, $y, $z)")
    }

    // In for loops
    for ((x, y, z) in points) {
        println("Coordinate: x=$x, y=$y, z=$z")
    }

    // Component functions
    val x3 = point.component1()
    val y3 = point.component2()
    val z3 = point.component3()
}
```

#### Data Class Requirements

```kotlin
//  Valid data classes

// 1. Primary constructor must have at least one parameter
data class ValidData1(val value: String)

// 2. All primary constructor parameters must be val or var
data class ValidData2(val id: Int, var name: String)

// 3. Can have secondary constructors
data class ValidData3(val id: Int, val name: String) {
    constructor(id: Int) : this(id, "Unknown")
}

// 4. Can have properties in body
data class ValidData4(val id: Int) {
    val computed: String = "ID: $id"
}

//  Invalid data classes

// Cannot be abstract
// abstract data class InvalidData1(val value: String) // Error

// Cannot be open
// open data class InvalidData2(val value: String) // Error

// Cannot be sealed
// sealed data class InvalidData3(val value: String) // Error

// Cannot be inner
class Outer {
    // inner data class InvalidData4(val value: String) // Error
}
```

#### Properties in Primary Constructor vs Body

```kotlin
data class Example(
    val id: String,        // Included in equals, hashCode, toString, copy
    val name: String       // Included in equals, hashCode, toString, copy
) {
    var status: String = ""  // NOT included in generated methods
    val computed: String = "$id-$name"  // NOT included

    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Example) return false
        // Only compares id and name
        return id == other.id && name == other.name
    }
}

fun demonstratePropertyDifference() {
    val ex1 = Example("1", "Test").apply { status = "Active" }
    val ex2 = Example("1", "Test").apply { status = "Inactive" }

    println(ex1 == ex2) // true (status not compared)
    println(ex1.toString()) // Example(id=1, name=Test) - status not shown
}
```

#### Limitations and Workarounds

```kotlin
// Limitation 1: Cannot inherit from data classes
data class BaseData(val id: String)
// data class DerivedData(val id: String, val name: String) : BaseData(id) // Error

// Workaround: Use interfaces or regular classes
interface HasId {
    val id: String
}

data class User(override val id: String, val name: String) : HasId
data class Product(override val id: String, val price: Double) : HasId

// Limitation 2: Body properties not included in generated methods
data class Person(val name: String) {
    var age: Int = 0  // Not in equals/hashCode
}

// Workaround: Put all important properties in constructor
data class PersonFixed(val name: String, val age: Int)

// Limitation 3: No control over generated methods
data class Account(val id: String, val balance: Double)

// Workaround: Override if needed
data class AccountCustom(val id: String, val balance: Double) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is AccountCustom) return false
        return id == other.id // Compare only ID
    }

    override fun hashCode(): Int = id.hashCode()
}
```

#### Best Practices

```kotlin
// 1. Use val for immutability
data class ImmutableUser(
    val id: String,
    val name: String,
    val email: String
)

// 2. Provide default values when appropriate
data class Configuration(
    val timeout: Long = 5000,
    val retries: Int = 3,
    val debug: Boolean = false
)

// 3. Use data classes for DTOs (Data Transfer Objects)
data class ApiResponse<T>(
    val data: T?,
    val error: String?,
    val timestamp: Long = System.currentTimeMillis()
)

// 4. Use data classes for state representation
sealed class UiState
data class Loading(val message: String = "") : UiState()
data class Success(val data: List<String>) : UiState()
data class Error(val message: String) : UiState()

// 5. Keep data classes simple and focused
//  Good: Simple data container
data class UserProfile(
    val id: String,
    val name: String,
    val email: String
)

//  Bad: Business logic in data class
data class BadUser(val id: String, val name: String) {
    fun validateEmail(): Boolean { /* logic */ return true }
    fun sendNotification() { /* logic */ }
}

//  Better: Separate concerns
data class User(val id: String, val name: String, val email: String)

class UserService {
    fun validateEmail(user: User): Boolean = user.email.contains("@")
    fun sendNotification(user: User) { /* logic */ }
}
```

#### Common Use Cases

```kotlin
// 1. API responses
data class UserResponse(
    val id: String,
    val username: String,
    val email: String,
    val createdAt: String
)

// 2. Database entities
data class UserEntity(
    val id: Long,
    val name: String,
    val email: String,
    val createdAt: Long
)

// 3. Configuration objects
data class DatabaseConfig(
    val host: String,
    val port: Int,
    val database: String,
    val username: String,
    val password: String
)

// 4. Event objects
data class UserClickedEvent(
    val userId: String,
    val elementId: String,
    val timestamp: Long
)

// 5. Value objects
data class Money(
    val amount: Double,
    val currency: String
) {
    operator fun plus(other: Money): Money {
        require(currency == other.currency) { "Currency mismatch" }
        return Money(amount + other.amount, currency)
    }
}

// 6. Result types
sealed class Result<out T>
data class Success<T>(val value: T) : Result<T>()
data class Failure(val error: Throwable) : Result<Nothing>()
object Loading : Result<Nothing>()
```

---

## Русский

[Full Russian translation...]

---

## Follow-ups

1. Why can't data classes be open or abstract?
2. How does copy() handle deep copying of nested objects?
3. What's the performance impact of using data classes vs regular classes?
4. Can data classes implement interfaces?
5. How do data classes work with serialization libraries?
6. What happens if you override equals() but not hashCode()?
7. Can data classes have generic type parameters?
8. How do data classes compare to Java records?

## References

- [Kotlin Documentation - Data Classes](https://kotlinlang.org/docs/data-classes.html)
- [Kotlin Language Specification - Data Classes](https://kotlinlang.org/spec/declarations.html#data-class-declaration)

## Related Questions

- [[q-sealed-class-sealed-interface--kotlin--medium]]
- [[q-value-classes-inline-classes--kotlin--medium]]
- [[q-class-initialization-order--kotlin--medium]]
- [[q-kotlin-immutability--kotlin--medium]]

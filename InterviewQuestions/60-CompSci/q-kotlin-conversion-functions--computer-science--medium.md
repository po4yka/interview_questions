---
id: 20251012-12271111117
title: "Kotlin Conversion Functions / Kotlin Conversion Функции"
aliases: []
topic: computer-science
subtopics: [type-system, class-features, null-safety]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-coroutine-cancellation-mechanisms--kotlin--medium, q-kotlin-property-delegates--programming-languages--medium, q-coroutine-dispatchers--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags:
  - 
  - difficulty/medium
---
# Как в Kotlin называется функция, которая вызывается на объекте для преобразования его в другой тип?

# Question (EN)
> What is the function called in Kotlin that is invoked on an object to convert it to another type?

# Вопрос (RU)
> Как в Kotlin называется функция, которая вызывается на объекте для преобразования его в другой тип?

---

## Answer (EN)

The function that is called on an object to convert it to another type in Kotlin is called an **extension function**. However, if you mean converting one data type to another, this can be implemented through a **converter function** or a method that returns a new object of the required type.

More specifically, these are **conversion functions** (often called **"to" functions**) that follow the pattern `toTargetType()`.

## Conversion Function Patterns

### 1. Built-in Conversion Functions

Kotlin's standard library provides many `toXxx()` conversion functions:

```kotlin
// Number conversions
val int = 42
val long = int.toLong()           // Int → Long
val double = int.toDouble()       // Int → Double
val string = int.toString()       // Int → String

// String conversions
val str = "123"
val num = str.toInt()             // String → Int
val numOrNull = str.toIntOrNull() // String → Int? (null if invalid)
val float = str.toFloat()         // String → Float

// Collection conversions
val list = listOf(1, 2, 3)
val set = list.toSet()            // List → Set
val array = list.toTypedArray()   // List → Array
val mutableList = list.toMutableList()  // List → MutableList
```

---

### 2. Extension Functions for Custom Conversions

You can create custom conversion extension functions:

```kotlin
// Domain models
data class User(val id: Int, val name: String, val email: String)
data class UserDto(val id: Int, val name: String)

// Extension function for conversion
fun User.toDto(): UserDto {
    return UserDto(
        id = this.id,
        name = this.name
    )
}

// Usage
val user = User(1, "Alice", "alice@example.com")
val dto = user.toDto()  // User → UserDto
```

**Naming convention:** Use `toTargetType()` for conversions:

```kotlin
fun String.toUser(): User {
    val parts = this.split(",")
    return User(
        id = parts[0].toInt(),
        name = parts[1],
        email = parts[2]
    )
}

val userString = "1,Alice,alice@example.com"
val user = userString.toUser()
```

---

### 3. Explicit Type Conversion (Casting)

For type casting (not conversion), Kotlin uses different operators:

```kotlin
// Safe cast (returns null if fails)
val str: String? = obj as? String

// Unsafe cast (throws exception if fails)
val str: String = obj as String

// Type check
if (obj is String) {
    // obj is smart-cast to String
    println(obj.length)
}
```

---

## Common Conversion Patterns

### Number Conversions

```kotlin
val byte: Byte = 10
val short: Short = byte.toShort()
val int: Int = byte.toInt()
val long: Long = byte.toLong()
val float: Float = byte.toFloat()
val double: Double = byte.toDouble()

// No automatic widening in Kotlin!
val x: Int = 100
// val y: Long = x  // - Compilation error
val y: Long = x.toLong()  // - Explicit conversion required
```

---

### String Conversions

```kotlin
// To String
val num = 42
val str = num.toString()        // "42"
val hex = num.toString(16)      // "2a" (hexadecimal)
val binary = num.toString(2)    // "101010" (binary)

// From String
val s = "123"
val int = s.toInt()             // 123
val long = s.toLong()           // 123L
val double = s.toDouble()       // 123.0

// Safe conversion
val invalid = "abc"
val num1 = invalid.toIntOrNull()     // null (doesn't throw)
val num2 = invalid.toInt()           // - NumberFormatException
```

---

### Collection Conversions

```kotlin
// To different collection types
val list = listOf(1, 2, 3, 2, 1)
val set = list.toSet()              // [1, 2, 3] (duplicates removed)
val array = list.toTypedArray()     // Array<Int>
val intArray = list.toIntArray()    // IntArray (primitive)

// Mutability conversions
val immutableList = listOf(1, 2, 3)
val mutableList = immutableList.toMutableList()
mutableList.add(4)  // Now can modify

val mutableSet = mutableSetOf(1, 2)
val immutableSet = mutableSet.toSet()  // Immutable copy
```

---

### Map Conversions

```kotlin
// List to Map
val users = listOf(
    User(1, "Alice", "alice@example.com"),
    User(2, "Bob", "bob@example.com")
)

val userMap = users.associateBy { it.id }
// Map: {1=User(1, Alice), 2=User(2, Bob)}

// Map to List
val map = mapOf(1 to "one", 2 to "two")
val list = map.toList()  // List<Pair<Int, String>>
val entries = map.entries.toList()  // List of Map.Entry
```

---

### Custom Domain Conversions

```kotlin
// Entity to DTO
data class UserEntity(
    val id: Int,
    val firstName: String,
    val lastName: String,
    val email: String,
    val passwordHash: String
)

data class UserResponse(
    val id: Int,
    val fullName: String,
    val email: String
)

fun UserEntity.toResponse(): UserResponse {
    return UserResponse(
        id = this.id,
        fullName = "$firstName $lastName",
        email = this.email
        // passwordHash is NOT included (security)
    )
}

// Usage
val entity = UserEntity(1, "Alice", "Smith", "alice@example.com", "hash123")
val response = entity.toResponse()
```

---

### JSON Conversions (with libraries)

```kotlin
// Using kotlinx.serialization
import kotlinx.serialization.*
import kotlinx.serialization.json.*

@Serializable
data class User(val name: String, val age: Int)

val json = Json.encodeToString(user)  // User → JSON String
val user = Json.decodeFromString<User>(json)  // JSON String → User
```

---

## Operator Functions for Conversion

Kotlin also has **operator functions** for implicit conversions:

```kotlin
class Temperature(val celsius: Double) {
    // Conversion to Double
    operator fun invoke(): Double = celsius

    // Allow Temperature + Double
    operator fun plus(degrees: Double) = Temperature(celsius + degrees)
}

val temp = Temperature(25.0)
val value: Double = temp()  // Calling invoke()
```

---

## Best Practices

### 1. Use Descriptive Names

```kotlin
// - GOOD - Clear intent
fun User.toDto(): UserDto
fun UserDto.toEntity(): User
fun String.toBase64(): String
fun ByteArray.toHexString(): String

// - BAD - Unclear
fun User.convert(): UserDto
fun transform(user: User): UserDto
```

### 2. Null Safety with Conversions

```kotlin
// - GOOD - Use xxxOrNull for safe conversions
val age = ageString.toIntOrNull() ?: 0

// - RISKY - Can throw exception
val age = ageString.toInt()  // NumberFormatException if invalid
```

### 3. Extension Functions for Domain Conversions

```kotlin
// - GOOD - Extension function
fun Order.toOrderResponse(): OrderResponse {
    return OrderResponse(/* ... */)
}

// Usage reads naturally
val response = order.toOrderResponse()

// - Less natural - utility function
fun convertOrderToResponse(order: Order): OrderResponse {
    return OrderResponse(/* ... */)
}

val response = convertOrderToResponse(order)
```

### 4. Batch Conversions

```kotlin
// Convert collections
val users: List<User> = /* ... */
val dtos: List<UserDto> = users.map { it.toDto() }

// Or create extension
fun List<User>.toDtos(): List<UserDto> = map { it.toDto() }

val dtos = users.toDtos()
```

---

## Summary

**Conversion functions in Kotlin:**

1. **Built-in conversions** - `toInt()`, `toLong()`, `toString()`, `toList()`, etc.
2. **Extension functions** - Custom `toXxx()` methods for domain conversions
3. **Casting operators** - `as`, `as?` for type casting
4. **Operator functions** - `invoke()` for implicit conversions

**Naming pattern:**
- `toTargetType()` - for conversions
- `asTargetType()` - for casting/views (no data copy)

**Common uses:**
- Number type conversions
- String parsing
- Collection transformations
- Domain model conversions (Entity ↔ DTO)
- Serialization (Object ↔ JSON/XML)

**Best practice:** Use extension functions with `toXxx()` naming for clear, readable conversions.

---

## Ответ (RU)

Функция, которая вызывается на объекте для преобразования его в другой тип в Kotlin называется функцией расширения. Однако, если вы имеете в виду преобразование одного типа данных в другой тип, то это может быть реализовано через функцию-конвертер или метод, который возвращает новый объект нужного типа.

## Related Questions

- [[q-coroutine-cancellation-mechanisms--kotlin--medium]]
- [[q-kotlin-property-delegates--programming-languages--medium]]
- [[q-coroutine-dispatchers--kotlin--medium]]

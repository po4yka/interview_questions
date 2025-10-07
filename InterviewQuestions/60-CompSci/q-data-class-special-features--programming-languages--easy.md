---
tags:
  - copy
  - data-class
  - equals
  - hashcode
  - kotlin
  - programming-languages
  - tostring
difficulty: easy
status: draft
---

# Какая особенность у Data Class относительно других Kotlin Classes?

**English**: What is the special feature of Data Class compared to other Kotlin Classes?

## Answer

**Data classes** automatically generate several useful methods that you would otherwise have to write manually:

### Auto-Generated Methods

#### 1. equals()
**Compares object contents (not references):**

```kotlin
data class User(val name: String, val age: Int)

val user1 = User("John", 30)
val user2 = User("John", 30)
val user3 = User("Jane", 25)

println(user1 == user2)  // true (same content)
println(user1 == user3)  // false (different content)

// Regular class comparison
class Person(val name: String, val age: Int)

val p1 = Person("John", 30)
val p2 = Person("John", 30)
println(p1 == p2)  // false (compares references!)
```

#### 2. hashCode()
**Generates hash based on properties:**

```kotlin
data class User(val name: String, val age: Int)

val user1 = User("John", 30)
val user2 = User("John", 30)

println(user1.hashCode() == user2.hashCode())  // true

// Works correctly in HashSet/HashMap
val set = hashSetOf(user1)
println(set.contains(user2))  // true (finds by content)
```

#### 3. toString()
**Readable string representation:**

```kotlin
data class User(val name: String, val age: Int)

val user = User("John", 30)
println(user.toString())  // "User(name=John, age=30)"

// Regular class
class Person(val name: String, val age: Int)
val person = Person("John", 30)
println(person.toString())  // "Person@7a81197d" (not useful!)
```

#### 4. copy()
**Create modified copy:**

```kotlin
data class User(val name: String, val age: Int, val email: String)

val user = User("John", 30, "john@example.com")

// Copy with modifications
val olderUser = user.copy(age = 31)
println(olderUser)  // User(name=John, age=31, email=john@example.com)

// Copy specific properties
val renamed = user.copy(name = "Johnny")
println(renamed)  // User(name=Johnny, age=30, email=john@example.com)

// Full copy
val duplicate = user.copy()
```

#### 5. componentN() - Destructuring
**Unpack properties:**

```kotlin
data class User(val name: String, val age: Int, val email: String)

val user = User("John", 30, "john@example.com")

// Destructuring declaration
val (name, age, email) = user
println("$name is $age years old")  // "John is 30 years old"

// Can skip properties
val (userName, _) = user  // Ignore age
val (_, userAge, _) = user  // Only age

// Useful in loops
val users = listOf(
    User("John", 30, "john@example.com"),
    User("Jane", 25, "jane@example.com")
)

for ((name, age) in users) {
    println("$name: $age")
}
```

### Comparison: Data Class vs Regular Class

**Regular class:**
```kotlin
class Person(val name: String, val age: Int) {
    // Must manually override
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Person) return false
        return name == other.name && age == other.age
    }

    override fun hashCode(): Int {
        var result = name.hashCode()
        result = 31 * result + age
        return result
    }

    override fun toString(): String {
        return "Person(name=$name, age=$age)"
    }

    // copy() not available
    // componentN() not available
}
```

**Data class:**
```kotlin
// All methods auto-generated!
data class Person(val name: String, val age: Int)
```

### Use Cases

**Perfect for:**
- DTOs (Data Transfer Objects)
- API responses
- Database entities
- Configuration objects
- Immutable state

```kotlin
// API response
data class UserResponse(
    val id: Int,
    val name: String,
    val email: String
)

// Database entity
data class TodoItem(
    val id: Long,
    val title: String,
    val completed: Boolean
)

// App state
data class UiState(
    val isLoading: Boolean,
    val data: List<Item>?,
    val error: String?
)
```

### Requirements

**Data class must have:**
- Primary constructor with at least one parameter
- All primary constructor parameters marked as `val` or `var`
- Cannot be `abstract`, `open`, `sealed`, or `inner`

```kotlin
// ✅ Valid
data class User(val name: String, val age: Int)

// ✅ Valid (var allowed)
data class MutableUser(var name: String, var age: Int)

// ❌ Invalid (no parameters)
data class Empty()  // Error!

// ❌ Invalid (parameters not in constructor)
data class Invalid {
    val name: String = ""  // Error!
}

// ❌ Invalid (open/abstract)
open data class OpenUser(val name: String)  // Error!
```

### Generated Methods Only Use Primary Constructor Properties

```kotlin
data class User(val name: String, val age: Int) {
    var address: String = ""  // Not in primary constructor
}

val user1 = User("John", 30).apply { address = "NYC" }
val user2 = User("John", 30).apply { address = "LA" }

// equals() ignores address (not in primary constructor)
println(user1 == user2)  // true

// copy() doesn't copy address
val copy = user1.copy()
println(copy.address)  // "" (empty, not "NYC")
```

### Summary

| Method | Purpose | Benefit |
|--------|---------|---------|
| `equals()` | Content comparison | Correct equality checks |
| `hashCode()` | Hash generation | Works in HashSet/HashMap |
| `toString()` | String representation | Easy debugging |
| `copy()` | Create modified copy | Immutability pattern |
| `componentN()` | Destructuring | Convenient unpacking |

**Data classes are convenient for storing data** and greatly simplify working with **immutable structures**.

## Ответ

Data Class автоматически генерирует equals, hashCode, toString, copy и componentN функции. Они удобны для хранения данных и значительно упрощают работу с неизменяемыми структурами.


---
tags:
  - programming-languages
difficulty: easy
---

# How many instance types does Nothing have?

**English**: How many instance types does the Nothing type have in Kotlin?

## Answer

**Nothing has no instances.** It is an uninhabited type that cannot be instantiated.

**Key characteristics:**
- Nothing is a type that has no values
- It is the subtype of all types (bottom type)
- Used to represent functions that never return normally
- Used to represent expressions that never complete
- Commonly used with functions that always throw exceptions or run infinite loops

**When Nothing is used:**
- Functions that always throw exceptions (`throw`, `error()`, `TODO()`)
- Functions with infinite loops
- Expressions that never produce a value
- As a type parameter for empty collections

### Code Examples

**Functions that return Nothing:**

```kotlin
// Function that always throws - returns Nothing
fun fail(message: String): Nothing {
    throw IllegalStateException(message)
}

// Function with infinite loop - returns Nothing
fun infiniteLoop(): Nothing {
    while (true) {
        println("Running forever...")
        Thread.sleep(1000)
    }
}

// Built-in functions that return Nothing
fun demonstrateBuiltIn() {
    TODO("Not implemented yet")  // Returns Nothing
    error("Something went wrong")  // Returns Nothing
}

fun main() {
    // These functions never return a value
    // fail("Error occurred")  // Would throw exception
    // infiniteLoop()  // Would run forever
}
```

**Nothing in type hierarchy:**

```kotlin
fun processValue(value: String?): Int {
    // Nothing is a subtype of Int, so this compiles
    val length: Int = value?.length ?: fail("Value is null")
    return length
}

fun getUser(id: Int): User {
    // Nothing is a subtype of User
    return findUser(id) ?: error("User not found")
}

data class User(val id: Int, val name: String)

fun findUser(id: Int): User? = null  // Simulate database lookup

fun main() {
    try {
        val length = processValue(null)
        println(length)
    } catch (e: Exception) {
        println("Caught: ${e.message}")
    }
}
```

**Nothing with when expressions:**

```kotlin
sealed class Result {
    data class Success(val value: Int) : Result()
    data class Error(val message: String) : Result()
}

fun handleResult(result: Result): Int {
    return when (result) {
        is Result.Success -> result.value
        is Result.Error -> error(result.message)  // Returns Nothing
    }
}

fun main() {
    val success = Result.Success(42)
    println(handleResult(success))  // 42

    val failure = Result.Error("Something went wrong")
    try {
        handleResult(failure)  // Throws exception
    } catch (e: Exception) {
        println("Error handled: ${e.message}")
    }
}
```

**Nothing in collections:**

```kotlin
fun main() {
    // Empty list has type List<Nothing>
    val emptyList: List<Nothing> = emptyList()
    println("Empty list size: ${emptyList.size}")  // 0

    // Nothing is a subtype of all types
    val strings: List<String> = emptyList  // Works!
    val numbers: List<Int> = emptyList     // Works!
    val users: List<User> = emptyList      // Works!

    // listOf() returns List<Nothing> when empty
    val empty = listOf()
    println(empty::class)  // class kotlin.collections.EmptyList
}

data class User(val name: String)
```

**Nothing? (nullable Nothing):**

```kotlin
fun main() {
    // Nothing? can only hold null
    val nothingNullable: Nothing? = null
    println(nothingNullable)  // null

    // This is the only valid value for Nothing?
    // val invalid: Nothing? = something  // No other value possible!

    // Often used as a type parameter for functions that return null
    fun alwaysNull(): Nothing? = null

    val result = alwaysNull()
    println(result)  // null
}
```

**Practical usage with TODO():**

```kotlin
interface UserRepository {
    fun getUser(id: Int): User
    fun saveUser(user: User)
    fun deleteUser(id: Int): Boolean
}

data class User(val id: Int, val name: String)

class UserRepositoryImpl : UserRepository {
    override fun getUser(id: Int): User {
        TODO("Implement database query")  // Returns Nothing
    }

    override fun saveUser(user: User) {
        TODO("Implement save operation")
    }

    override fun deleteUser(id: Int): Boolean {
        TODO("Implement delete operation")
    }
}

fun main() {
    val repo = UserRepositoryImpl()

    try {
        val user = repo.getUser(1)
    } catch (e: NotImplementedError) {
        println("Function not implemented: ${e.message}")
    }
}
```

**Nothing vs Unit:**

```kotlin
// Unit: Function completes normally, returns nothing useful
fun printMessage(msg: String): Unit {
    println(msg)
    // Implicitly returns Unit
}

// Nothing: Function never completes normally
fun failWithError(msg: String): Nothing {
    throw Exception(msg)
    // Never returns
}

fun demonstrateDifference() {
    // Unit function completes
    printMessage("Hello")  // Prints and continues
    println("After printMessage")

    // Nothing function never returns
    // failWithError("Error")  // Would throw and never reach next line
    // println("After failWithError")  // Unreachable code
}

fun main() {
    demonstrateDifference()
}
```

**Type inference with Nothing:**

```kotlin
fun checkValue(value: Int?): Int {
    // Compiler knows that if value is null, fail() throws
    // So the return type can be inferred as Int (not Int?)
    return value ?: fail("Value cannot be null")
}

fun fail(message: String): Nothing {
    throw IllegalArgumentException(message)
}

fun main() {
    println(checkValue(42))  // 42

    try {
        println(checkValue(null))  // Throws exception
    } catch (e: Exception) {
        println("Caught: ${e.message}")
    }
}
```

---

## Ответ

### Вопрос
Сколько типов инстансов у Nothing

### Ответ
Nothing не имеет инстансов.

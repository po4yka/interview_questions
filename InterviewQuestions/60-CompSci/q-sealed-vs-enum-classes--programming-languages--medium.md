---
tags:
  - comparison
  - enum
  - kotlin
  - oop
  - programming-languages
  - sealed-class
difficulty: medium
status: draft
---

# Каковы отличия sealed и enum классов в Kotlin?

**English**: What are the differences between sealed and enum classes in Kotlin?

## Answer

### Key Differences

| Feature | Enum Class | Sealed Class |
|---------|-----------|--------------|
| **Structure** | Fixed set of homogeneous objects | Restricted class hierarchy |
| **Instance count** | Fixed at compile time | Can create multiple instances |
| **Properties** | All instances have same structure | Subclasses can have different properties |
| **Inheritance** | Cannot have subclasses | Can have multiple subclasses |
| **Use case** | Simple fixed values | Complex states with different data |

### Enum Class

**Fixed set of homogeneous objects with identical structure:**

```kotlin
enum class Color(val rgb: Int) {
    RED(0xFF0000),
    GREEN(0x00FF00),
    BLUE(0x0000FF);

    fun hex() = "#${rgb.toString(16)}"
}

// Usage
val color = Color.RED
println(color.rgb)  // 16711680
println(color.hex()) // #ff0000

// All enum instances have same structure
when (color) {
    Color.RED -> println("Red")
    Color.GREEN -> println("Green")
    Color.BLUE -> println("Blue")
    // Exhaustive: compiler knows all values
}
```

**Characteristics:**
- Each value is a single instance
- All values have same properties
- Cannot create new instances at runtime
- Can iterate over all values: `Color.values()`

### Sealed Class

**Restricted hierarchy where subclasses can have different structures:**

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T, val timestamp: Long) : Result<T>()
    data class Error(val exception: Exception, val code: Int) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Usage - different properties per subclass
val result: Result<User> = Result.Success(user, System.currentTimeMillis())

when (result) {
    is Result.Success -> println("Data: ${result.data}, time: ${result.timestamp}")
    is Result.Error -> println("Error: ${result.exception.message}, code: ${result.code}")
    is Result.Loading -> println("Loading...")
    // Exhaustive: compiler knows all subclasses
}

// Can create multiple Success instances with different data
val result1 = Result.Success("data1", 123L)
val result2 = Result.Success("data2", 456L)
```

**Characteristics:**
- Multiple instances of each subclass allowed
- Subclasses can have completely different properties
- Can have data classes, objects, regular classes as subclasses
- Cannot create instances of sealed class itself

### When to Use Each

**Use `enum class` when:**
- Fixed set of values that won't change
- All values have same structure
- Simple states or constants
- Need to iterate over all values

```kotlin
enum class Direction { NORTH, SOUTH, EAST, WEST }
enum class HttpStatus(val code: Int) { OK(200), NOT_FOUND(404), ERROR(500) }
enum class DayOfWeek { MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY }
```

**Use `sealed class` when:**
- Complex states with different structures
- Each state has different parameters
- Need type-safe state machine
- Modeling discriminated unions

```kotlin
// Network result with different data per state
sealed class NetworkResult<out T> {
    data class Success<T>(val data: T, val cached: Boolean) : NetworkResult<T>()
    data class Error(val message: String, val retryable: Boolean) : NetworkResult<Nothing>()
    object Loading : NetworkResult<Nothing>()
}

// UI state with different properties
sealed class UiState {
    object Idle : UiState()
    object Loading : UiState()
    data class Success(val items: List<Item>, val hasMore: Boolean) : UiState()
    data class Error(val error: Throwable, val canRetry: Boolean) : UiState()
}
```

### Can Combine Both

```kotlin
// Enum for simple status
enum class Status { PENDING, COMPLETED, FAILED }

// Sealed class for complex result with enum
sealed class TaskResult {
    data class Success(val value: String, val status: Status) : TaskResult()
    data class Failure(val error: String, val status: Status) : TaskResult()
}
```

## Ответ

sealed class – это ограниченная иерархия классов, где можно создавать разные подклассы с разными свойствами. enum class – это фиксированный набор однотипных объектов, которые не имеют разной структуры. enum class используется для фиксированного набора значений, когда значения не изменятся и у всех одинаковая структура. sealed class используется для сложных состояний с разной структурой, когда у состояний разные параметры и поведение.


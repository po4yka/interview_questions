---
tags:
  - data-class
  - kotlin
  - oop
  - programming-languages
  - sealed-class
  - type-safety
  - when-expressions
difficulty: medium
---

# Расскажи data классы и sealed классы

**English**: Tell me about data classes and sealed classes

## Answer

### Data Classes

Data classes are designed for **storing data** and automatically generate useful methods:
- `equals()` - value-based equality
- `hashCode()` - consistent hashing
- `toString()` - readable string representation
- `copy()` - create modified copies

```kotlin
data class User(val name: String, val age: Int)

val user1 = User("John", 30)
val user2 = user1.copy(age = 31)
```

### Sealed Classes

Sealed classes represent **restricted inheritance hierarchies** where all possible subclasses are known at compile time:

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val error: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}
```

### Combining Both

Together, they create **type-safe and easily manageable data structures**, especially for `when` expressions:

```kotlin
fun handleResult(result: Result<String>) = when (result) {
    is Result.Success -> println("Data: ${result.data}")
    is Result.Error -> println("Error: ${result.error}")
    Result.Loading -> println("Loading...")
}  // Exhaustive - compiler checks all cases!
```

**Benefits of combination:**
- Type safety at compile time
- Exhaustive when expressions
- Clean, maintainable code
- Perfect for state management

## Ответ

Data классы в Kotlin предназначены для хранения данных и автоматически генерируют методы equals(), hashCode(), toString(), а также copy()...


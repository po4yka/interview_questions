---
tags:
  - programming-languages
difficulty: medium
status: reviewed
---

# What is known about data classes and sealed classes?

**English**: What is known about data classes and sealed classes in Kotlin?

## Answer

**Data Classes:**
Data classes are designed for storing data and automatically generate several useful methods:
- `equals()` - for content-based equality comparison
- `hashCode()` - for hash-based collections
- `toString()` - for string representation
- `copy()` - for creating copies with modified properties
- `componentN()` - component functions for destructuring

Data classes are commonly used as data models in applications, DTOs (Data Transfer Objects), and POJO (Plain Old Java Objects).

**Sealed Classes:**
Sealed classes restrict subclass creation to the same file (or module in Kotlin 1.5+) and are used to create type-safe hierarchies:
- All possible subclasses are known at compile time
- Perfect for representing restricted class hierarchies
- Excellent with `when` expressions (exhaustive checking)
- Often used for state management in architectural components

Both are frequently used in Android development - data classes for models and sealed classes for managing states.

### Code Examples

**Data class example:**
```kotlin
// Simple data class
data class User(
    val id: Int,
    val name: String,
    val email: String,
    val age: Int
)

fun main() {
    val user1 = User(1, "Alice", "alice@example.com", 30)
    val user2 = User(1, "Alice", "alice@example.com", 30)
    val user3 = User(2, "Bob", "bob@example.com", 25)

    // Automatic equals() implementation
    println(user1 == user2)  // true (same content)
    println(user1 == user3)  // false (different content)

    // Automatic toString()
    println(user1)  // User(id=1, name=Alice, email=alice@example.com, age=30)

    // Automatic hashCode()
    val userSet = setOf(user1, user2, user3)
    println(userSet.size)  // 2 (user1 and user2 are equal)

    // copy() function
    val olderUser = user1.copy(age = 31)
    println(olderUser)  // User(id=1, name=Alice, email=alice@example.com, age=31)

    // Destructuring with componentN()
    val (id, name, email, age) = user1
    println("$name is $age years old")  // Alice is 30 years old
}
```

**Data class as DTO/Model:**
```kotlin
// Response model from API
data class ApiResponse(
    val success: Boolean,
    val message: String,
    val data: List<User>?
)

data class User(
    val id: Int,
    val username: String,
    val isActive: Boolean
)

fun parseApiResponse(json: String): ApiResponse {
    // Parse JSON and return
    return ApiResponse(
        success = true,
        message = "Users fetched successfully",
        data = listOf(
            User(1, "alice", true),
            User(2, "bob", false)
        )
    )
}

fun main() {
    val response = parseApiResponse("{}")
    println(response)

    response.data?.forEach { user ->
        println("User: ${user.username}, Active: ${user.isActive}")
    }
}
```

**Sealed class example:**
```kotlin
// Sealed class for UI state
sealed class UiState {
    object Loading : UiState()
    data class Success(val data: List<String>) : UiState()
    data class Error(val message: String, val code: Int) : UiState()
    object Empty : UiState()
}

// Handling all possible states
fun renderUi(state: UiState) {
    when (state) {
        is UiState.Loading -> println("Showing loading spinner...")
        is UiState.Success -> println("Displaying data: ${state.data}")
        is UiState.Error -> println("Error ${state.code}: ${state.message}")
        is UiState.Empty -> println("No data available")
        // No else needed - compiler knows all cases are covered
    }
}

fun main() {
    renderUi(UiState.Loading)
    renderUi(UiState.Success(listOf("Item 1", "Item 2")))
    renderUi(UiState.Error("Network error", 500))
    renderUi(UiState.Empty)
}
```

**Sealed class for network result:**
```kotlin
sealed class NetworkResult<out T> {
    data class Success<T>(val data: T) : NetworkResult<T>()
    data class Error(val exception: Exception) : NetworkResult<Nothing>()
    object Loading : NetworkResult<Nothing>()
}

data class Product(val id: Int, val name: String, val price: Double)

fun fetchProducts(): NetworkResult<List<Product>> {
    return try {
        // Simulate API call
        val products = listOf(
            Product(1, "Laptop", 999.99),
            Product(2, "Mouse", 29.99)
        )
        NetworkResult.Success(products)
    } catch (e: Exception) {
        NetworkResult.Error(e)
    }
}

fun handleResult(result: NetworkResult<List<Product>>) {
    when (result) {
        is NetworkResult.Success -> {
            println("Fetched ${result.data.size} products:")
            result.data.forEach { product ->
                println("  ${product.name}: $${product.price}")
            }
        }
        is NetworkResult.Error -> {
            println("Error: ${result.exception.message}")
        }
        NetworkResult.Loading -> {
            println("Loading products...")
        }
    }
}

fun main() {
    val result = fetchProducts()
    handleResult(result)
}
```

**Combining data classes with sealed classes:**
```kotlin
// Sealed class with data class subclasses
sealed class Result {
    data class Success(val value: Int) : Result()
    data class Failure(val error: String) : Result()
}

fun divide(a: Int, b: Int): Result {
    return if (b != 0) {
        Result.Success(a / b)
    } else {
        Result.Failure("Division by zero")
    }
}

fun main() {
    val result1 = divide(10, 2)
    val result2 = divide(10, 0)

    when (result1) {
        is Result.Success -> println("Result: ${result1.value}")
        is Result.Failure -> println("Error: ${result1.error}")
    }

    when (result2) {
        is Result.Success -> println("Result: ${result2.value}")
        is Result.Failure -> println("Error: ${result2.error}")
    }
}
```

**Android ViewModel state example:**
```kotlin
// Typical usage in Android MVVM
data class UserProfile(
    val name: String,
    val email: String,
    val avatarUrl: String
)

sealed class ProfileState {
    object Initial : ProfileState()
    object Loading : ProfileState()
    data class Success(val profile: UserProfile) : ProfileState()
    data class Error(val message: String) : ProfileState()
}

class ProfileViewModel {
    private var state: ProfileState = ProfileState.Initial

    fun loadProfile() {
        state = ProfileState.Loading
        // Simulate loading
        state = ProfileState.Success(
            UserProfile(
                name = "Alice",
                email = "alice@example.com",
                avatarUrl = "https://example.com/avatar.jpg"
            )
        )
    }

    fun getState() = state
}

fun main() {
    val viewModel = ProfileViewModel()

    when (val state = viewModel.getState()) {
        is ProfileState.Initial -> println("Not loaded yet")
        is ProfileState.Loading -> println("Loading...")
        is ProfileState.Success -> println("User: ${state.profile.name}")
        is ProfileState.Error -> println("Error: ${state.message}")
    }

    viewModel.loadProfile()

    when (val state = viewModel.getState()) {
        is ProfileState.Success -> {
            val (name, email, avatarUrl) = state.profile
            println("Name: $name, Email: $email")
        }
        else -> println("Not successful")
    }
}
```

---

## Ответ

### Вопрос
Что известно о data классах и sealed классах ?

### Ответ
Data классы предназначены для хранения данных и автоматически генерируют методы equals(), hashCode(), toString(), copy() и компонентные функции. Sealed классы ограничивают создание подклассов только внутри того же файла и используются для создания безопасных по типам иерархий. Data классы часто применяются как модели данных, а sealed классы — для управления состояниями в архитектурных компонентах.

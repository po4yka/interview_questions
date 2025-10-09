---
tags:
  - programming-languages
difficulty: medium
status: reviewed
---

# What are data classes and sealed classes used for?

**English**: What are data classes and sealed classes used for in Kotlin?

## Answer

**data class** — Used for storing and working with data. Convenient for copying, logical comparison, and serialization.

**sealed class** — Used for a restricted set of subtypes. Convenient when using `when` expressions, as all cases must be handled — this increases safety and readability.

**Key use cases:**
- data class: DTOs, models, API responses, database entities, configuration
- sealed class: State management, result types, navigation, error handling

### Code Examples

**data class for data storage:**

```kotlin
// API response model
data class UserResponse(
    val id: Int,
    val username: String,
    val email: String,
    val isActive: Boolean
)

// Easy copying with modifications
fun demonstrateCopying() {
    val user = UserResponse(1, "alice", "alice@example.com", true)

    // Create modified copy
    val deactivatedUser = user.copy(isActive = false)
    val renamedUser = user.copy(username = "alice_smith")

    println(user)               // Original unchanged
    println(deactivatedUser)    // Only isActive changed
    println(renamedUser)        // Only username changed
}

fun main() {
    demonstrateCopying()
}
```

**data class for logical comparison:**

```kotlin
data class Point(val x: Int, val y: Int)

data class Order(
    val id: String,
    val items: List<String>,
    val total: Double
)

fun demonstrateComparison() {
    // Simple comparison
    val p1 = Point(10, 20)
    val p2 = Point(10, 20)
    val p3 = Point(15, 25)

    println("p1 == p2: ${p1 == p2}")  // true - content equality
    println("p1 === p2: ${p1 === p2}")  // false - different references
    println("p1 == p3: ${p1 == p3}")  // false - different values

    // Complex objects
    val order1 = Order("ORD-001", listOf("Laptop", "Mouse"), 1029.99)
    val order2 = Order("ORD-001", listOf("Laptop", "Mouse"), 1029.99)

    println("order1 == order2: ${order1 == order2}")  // true

    // Works in collections
    val uniqueOrders = setOf(order1, order2)
    println("Unique orders: ${uniqueOrders.size}")  // 1
}

fun main() {
    demonstrateComparison()
}
```

**data class for serialization:**

```kotlin
import kotlinx.serialization.*
import kotlinx.serialization.json.*

@Serializable
data class Product(
    val id: Int,
    val name: String,
    val price: Double,
    val inStock: Boolean
)

@Serializable
data class CartItem(
    val product: Product,
    val quantity: Int
)

fun demonstrateSerialization() {
    val product = Product(1, "Laptop", 999.99, true)
    val item = CartItem(product, 2)

    // Serialize to JSON
    val json = Json.encodeToString(item)
    println("JSON: $json")

    // Deserialize from JSON
    val restored = Json.decodeFromString<CartItem>(json)
    println("Restored: $restored")

    // Works because of equals()
    println("Equal: ${item == restored}")  // true
}

fun main() {
    demonstrateSerialization()
}
```

**sealed class for when expression:**

```kotlin
sealed class Operation {
    data class Add(val a: Int, val b: Int) : Operation()
    data class Subtract(val a: Int, val b: Int) : Operation()
    data class Multiply(val a: Int, val b: Int) : Operation()
    data class Divide(val a: Int, val b: Int) : Operation()
}

fun calculate(operation: Operation): Double {
    // All cases must be handled - compiler enforces this!
    return when (operation) {
        is Operation.Add -> (operation.a + operation.b).toDouble()
        is Operation.Subtract -> (operation.a - operation.b).toDouble()
        is Operation.Multiply -> (operation.a * operation.b).toDouble()
        is Operation.Divide -> {
            if (operation.b != 0) {
                operation.a.toDouble() / operation.b
            } else {
                Double.NaN
            }
        }
        // No else needed - compiler knows all cases
    }
}

fun main() {
    println(calculate(Operation.Add(10, 5)))       // 15.0
    println(calculate(Operation.Subtract(10, 5)))  // 5.0
    println(calculate(Operation.Multiply(10, 5)))  // 50.0
    println(calculate(Operation.Divide(10, 5)))    // 2.0
    println(calculate(Operation.Divide(10, 0)))    // NaN
}
```

**sealed class for safety and readability:**

```kotlin
// Type-safe state management
sealed class UiState<out T> {
    object Initial : UiState<Nothing>()
    object Loading : UiState<Nothing>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String, val code: Int? = null) : UiState<Nothing>()
}

class ViewModel {
    private var state: UiState<List<String>> = UiState.Initial

    fun loadData() {
        state = UiState.Loading
        // Simulate loading
        try {
            val data = listOf("Item 1", "Item 2", "Item 3")
            state = UiState.Success(data)
        } catch (e: Exception) {
            state = UiState.Error(e.message ?: "Unknown error")
        }
    }

    fun getState() = state
}

// UI layer - type-safe handling
fun render(state: UiState<List<String>>) {
    when (state) {
        UiState.Initial -> {
            println("Press button to load data")
        }
        UiState.Loading -> {
            println("Loading...")
        }
        is UiState.Success -> {
            println("Data loaded:")
            state.data.forEach { println("  - $it") }
        }
        is UiState.Error -> {
            println("Error: ${state.message}")
            state.code?.let { println("Error code: $it") }
        }
    }
}

fun main() {
    val viewModel = ViewModel()

    render(viewModel.getState())  // Initial
    viewModel.loadData()
    render(viewModel.getState())  // Success
}
```

**Combined example: API client:**

```kotlin
// Data classes for requests/responses
@Serializable
data class LoginRequest(
    val username: String,
    val password: String
)

@Serializable
data class UserData(
    val id: Int,
    val username: String,
    val email: String,
    val token: String
)

// Sealed class for results
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val code: Int, val message: String) : ApiResult<Nothing>()
    object NetworkError : ApiResult<Nothing>()
}

class ApiClient {
    fun login(request: LoginRequest): ApiResult<UserData> {
        return try {
            // Simulate API call
            if (request.username == "admin" && request.password == "password") {
                ApiResult.Success(
                    UserData(
                        id = 1,
                        username = request.username,
                        email = "admin@example.com",
                        token = "abc123xyz"
                    )
                )
            } else {
                ApiResult.Error(401, "Invalid credentials")
            }
        } catch (e: Exception) {
            ApiResult.NetworkError
        }
    }
}

fun handleLoginResult(result: ApiResult<UserData>) {
    when (result) {
        is ApiResult.Success -> {
            val user = result.data
            println("Login successful!")
            println("Welcome, ${user.username}")
            println("Token: ${user.token}")
        }
        is ApiResult.Error -> {
            println("Login failed: ${result.message} (code: ${result.code})")
        }
        ApiResult.NetworkError -> {
            println("Network error. Please check your connection.")
        }
    }
}

fun main() {
    val client = ApiClient()

    // Successful login
    val request1 = LoginRequest("admin", "password")
    val result1 = client.login(request1)
    handleLoginResult(result1)

    println()

    // Failed login
    val request2 = LoginRequest("admin", "wrong")
    val result2 = client.login(request2)
    handleLoginResult(result2)
}
```

**Real-world form validation:**

```kotlin
// Data class for form data
data class RegistrationForm(
    val username: String,
    val email: String,
    val password: String,
    val confirmPassword: String
)

// Sealed class for validation result
sealed class ValidationResult {
    data class Valid(val form: RegistrationForm) : ValidationResult()
    data class Invalid(val errors: Map<String, String>) : ValidationResult()
}

fun validateForm(form: RegistrationForm): ValidationResult {
    val errors = mutableMapOf<String, String>()

    if (form.username.length < 3) {
        errors["username"] = "Username must be at least 3 characters"
    }

    if (!form.email.contains("@")) {
        errors["email"] = "Invalid email format"
    }

    if (form.password.length < 8) {
        errors["password"] = "Password must be at least 8 characters"
    }

    if (form.password != form.confirmPassword) {
        errors["confirmPassword"] = "Passwords do not match"
    }

    return if (errors.isEmpty()) {
        ValidationResult.Valid(form)
    } else {
        ValidationResult.Invalid(errors)
    }
}

fun handleValidation(result: ValidationResult) {
    when (result) {
        is ValidationResult.Valid -> {
            val (username, email, password, _) = result.form
            println("Registration successful!")
            println("Username: $username")
            println("Email: $email")
        }
        is ValidationResult.Invalid -> {
            println("Validation errors:")
            result.errors.forEach { (field, error) ->
                println("  $field: $error")
            }
        }
    }
}

fun main() {
    val validForm = RegistrationForm(
        username = "alice",
        email = "alice@example.com",
        password = "securepass123",
        confirmPassword = "securepass123"
    )

    val invalidForm = RegistrationForm(
        username = "al",
        email = "invalid",
        password = "123",
        confirmPassword = "456"
    )

    println("Valid form:")
    handleValidation(validateForm(validForm))

    println("\nInvalid form:")
    handleValidation(validateForm(invalidForm))
}
```

---

## Ответ

### Вопрос
Для чего data-классы и sealed-классы используются

### Ответ
data class — для хранения и работы с данными, удобны при копировании, логическом сравнении, сериализации. sealed class — для ограниченного набора подтипов. Удобны при использовании when, так как все случаи должны быть обработаны — это повышает безопасность и читаемость.

---
tags:
  - programming-languages
difficulty: medium
status: reviewed
---

# Describe data classes and sealed classes

**English**: Describe data classes and sealed classes in Kotlin.

## Answer

**Data Classes:**
Data classes in Kotlin are designed for storing data and automatically generate methods such as `equals()`, `hashCode()`, `toString()`, and `copy()`. They are ideal for creating POJO/POCO objects (Plain Old Java/C# Objects).

**Key features of data classes:**
- Automatic generation of utility methods
- Built-in support for destructuring declarations
- Immutability support with `val` properties
- Easy object copying with modifications via `copy()`
- Perfect for DTOs, models, and value objects

**Sealed Classes:**
Sealed classes are used to represent a restricted set of types, similar to enumerations, but with the ability to have classes with different properties and methods. This helps ensure safe usage when working with types at compile time, improving error handling and branching logic.

**Key features of sealed classes:**
- Restricted class hierarchies
- Compile-time exhaustiveness checking in `when` expressions
- Type-safe representation of finite state
- Perfect for state management and result types
- All subclasses must be in same file/module

### Code Examples

**Data class comprehensive example:**

```kotlin
// Simple data class for user data
data class User(
    val id: Int,
    val username: String,
    val email: String,
    val age: Int
)

fun main() {
    val user = User(1, "alice", "alice@example.com", 30)

    // Automatic toString()
    println(user)
    // User(id=1, username=alice, email=alice@example.com, age=30)

    // Automatic equals()
    val sameUser = User(1, "alice", "alice@example.com", 30)
    println(user == sameUser)  // true

    // copy() for creating modified instances
    val olderUser = user.copy(age = 31)
    println(olderUser)
    // User(id=1, username=alice, email=alice@example.com, age=31)

    // Destructuring declaration
    val (id, username, email, age) = user
    println("User $username is $age years old")
}
```

**Data class as POJO/DTO:**

```kotlin
// API response model
data class LoginResponse(
    val success: Boolean,
    val token: String?,
    val userId: Int?,
    val message: String,
    val expiresAt: Long?
)

// Request model
data class LoginRequest(
    val username: String,
    val password: String,
    val rememberMe: Boolean = false
)

// Domain model
data class UserProfile(
    val id: Int,
    val firstName: String,
    val lastName: String,
    val email: String,
    val phoneNumber: String?,
    val address: Address?
)

data class Address(
    val street: String,
    val city: String,
    val state: String,
    val zipCode: String,
    val country: String
)

fun login(request: LoginRequest): LoginResponse {
    // Simulate login
    return if (request.username == "alice" && request.password == "password") {
        LoginResponse(
            success = true,
            token = "abc123xyz",
            userId = 1,
            message = "Login successful",
            expiresAt = System.currentTimeMillis() + 3600000
        )
    } else {
        LoginResponse(
            success = false,
            token = null,
            userId = null,
            message = "Invalid credentials",
            expiresAt = null
        )
    }
}

fun main() {
    val request = LoginRequest("alice", "password", true)
    val response = login(request)

    println("Login ${if (response.success) "successful" else "failed"}")
    println("Message: ${response.message}")
    response.token?.let { println("Token: $it") }
}
```

**Sealed class comprehensive example:**

```kotlin
// Sealed class for representing different states
sealed class NetworkState {
    object Idle : NetworkState()
    object Loading : NetworkState()
    data class Success(val data: String, val timestamp: Long) : NetworkState()
    data class Error(val exception: Throwable, val retryable: Boolean) : NetworkState()
}

// Function that handles all possible states
fun handleNetworkState(state: NetworkState) {
    when (state) {  // No else needed - compiler knows all cases
        NetworkState.Idle -> {
            println("Network is idle")
        }
        NetworkState.Loading -> {
            println("Loading data...")
        }
        is NetworkState.Success -> {
            println("Success! Data: ${state.data}")
            println("Received at: ${state.timestamp}")
        }
        is NetworkState.Error -> {
            println("Error: ${state.exception.message}")
            if (state.retryable) {
                println("You can retry this operation")
            }
        }
    }
}

fun main() {
    val states = listOf(
        NetworkState.Idle,
        NetworkState.Loading,
        NetworkState.Success("User data loaded", System.currentTimeMillis()),
        NetworkState.Error(Exception("Network timeout"), true)
    )

    states.forEach { state ->
        handleNetworkState(state)
        println("---")
    }
}
```

**Sealed class with different properties:**

```kotlin
// Payment method types - each with different properties
sealed class PaymentMethod {
    data class CreditCard(
        val cardNumber: String,
        val cardholderName: String,
        val expiryMonth: Int,
        val expiryYear: Int,
        val cvv: String
    ) : PaymentMethod()

    data class PayPal(
        val email: String,
        val verified: Boolean
    ) : PaymentMethod()

    data class BankTransfer(
        val accountNumber: String,
        val bankName: String,
        val routingNumber: String
    ) : PaymentMethod()

    object Cash : PaymentMethod()

    data class Cryptocurrency(
        val walletAddress: String,
        val currency: String
    ) : PaymentMethod()
}

fun processPayment(method: PaymentMethod, amount: Double) {
    when (method) {
        is PaymentMethod.CreditCard -> {
            println("Processing credit card payment of $$amount")
            println("Card ending in: ${method.cardNumber.takeLast(4)}")
            println("Cardholder: ${method.cardholderName}")
        }
        is PaymentMethod.PayPal -> {
            println("Processing PayPal payment of $$amount")
            println("PayPal account: ${method.email}")
            if (!method.verified) {
                println("Warning: Account not verified")
            }
        }
        is PaymentMethod.BankTransfer -> {
            println("Processing bank transfer of $$amount")
            println("Bank: ${method.bankName}")
            println("Account: ${method.accountNumber}")
        }
        PaymentMethod.Cash -> {
            println("Processing cash payment of $$amount")
            println("Please prepare exact change")
        }
        is PaymentMethod.Cryptocurrency -> {
            println("Processing crypto payment of $$amount")
            println("Currency: ${method.currency}")
            println("Wallet: ${method.walletAddress}")
        }
    }
}

fun main() {
    val payments = listOf(
        PaymentMethod.CreditCard("1234567890123456", "Alice Smith", 12, 2025, "123"),
        PaymentMethod.PayPal("alice@example.com", true),
        PaymentMethod.BankTransfer("9876543210", "Chase Bank", "021000021"),
        PaymentMethod.Cash,
        PaymentMethod.Cryptocurrency("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "BTC")
    )

    payments.forEachIndexed { index, method ->
        println("Payment ${index + 1}:")
        processPayment(method, 100.0)
        println()
    }
}
```

**Combining data classes with sealed classes:**

```kotlin
// Generic result type using sealed class and data classes
sealed class Result<out T> {
    data class Success<T>(val value: T) : Result<T>()
    data class Failure(val error: Error) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Error types
data class Error(
    val code: Int,
    val message: String,
    val details: Map<String, String> = emptyMap()
)

// Domain models
data class Article(
    val id: Int,
    val title: String,
    val content: String,
    val author: String,
    val publishedAt: Long
)

// Service layer
class ArticleService {
    fun fetchArticle(id: Int): Result<Article> {
        return try {
            // Simulate API call
            if (id > 0) {
                Result.Success(
                    Article(
                        id = id,
                        title = "Kotlin Best Practices",
                        content = "Here are some best practices...",
                        author = "John Doe",
                        publishedAt = System.currentTimeMillis()
                    )
                )
            } else {
                Result.Failure(
                    Error(404, "Article not found", mapOf("article_id" to id.toString()))
                )
            }
        } catch (e: Exception) {
            Result.Failure(
                Error(500, "Server error", mapOf("exception" to e.message.orEmpty()))
            )
        }
    }
}

// UI layer
fun displayArticle(result: Result<Article>) {
    when (result) {
        is Result.Success -> {
            val article = result.value
            println("Title: ${article.title}")
            println("Author: ${article.author}")
            println("Content: ${article.content}")
        }
        is Result.Failure -> {
            println("Error ${result.error.code}: ${result.error.message}")
            if (result.error.details.isNotEmpty()) {
                println("Details: ${result.error.details}")
            }
        }
        Result.Loading -> {
            println("Loading article...")
        }
    }
}

fun main() {
    val service = ArticleService()

    println("Fetching article 1:")
    val result1 = service.fetchArticle(1)
    displayArticle(result1)

    println("\nFetching article -1:")
    val result2 = service.fetchArticle(-1)
    displayArticle(result2)
}
```

**Real-world example: Form validation:**

```kotlin
// Form data (data class)
data class RegistrationForm(
    val username: String,
    val email: String,
    val password: String,
    val confirmPassword: String,
    val agreeToTerms: Boolean
)

// Validation result (sealed class)
sealed class ValidationResult {
    data class Valid(val form: RegistrationForm) : ValidationResult()
    data class Invalid(val errors: List<ValidationError>) : ValidationResult()
}

// Error types (data class)
data class ValidationError(
    val field: String,
    val message: String
)

fun validateRegistration(form: RegistrationForm): ValidationResult {
    val errors = mutableListOf<ValidationError>()

    if (form.username.length < 3) {
        errors.add(ValidationError("username", "Username must be at least 3 characters"))
    }

    if (!form.email.contains("@") || !form.email.contains(".")) {
        errors.add(ValidationError("email", "Invalid email format"))
    }

    if (form.password.length < 8) {
        errors.add(ValidationError("password", "Password must be at least 8 characters"))
    }

    if (form.password != form.confirmPassword) {
        errors.add(ValidationError("confirmPassword", "Passwords do not match"))
    }

    if (!form.agreeToTerms) {
        errors.add(ValidationError("agreeToTerms", "You must agree to terms"))
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
            println("Form is valid!")
            println("Registering user: ${result.form.username}")
            println("Email: ${result.form.email}")
        }
        is ValidationResult.Invalid -> {
            println("Form has ${result.errors.size} error(s):")
            result.errors.forEach { error ->
                println("  - ${error.field}: ${error.message}")
            }
        }
    }
}

fun main() {
    val validForm = RegistrationForm(
        username = "alice",
        email = "alice@example.com",
        password = "securepass123",
        confirmPassword = "securepass123",
        agreeToTerms = true
    )

    val invalidForm = RegistrationForm(
        username = "al",
        email = "invalid-email",
        password = "123",
        confirmPassword = "456",
        agreeToTerms = false
    )

    println("Validating valid form:")
    handleValidation(validateRegistration(validForm))

    println("\nValidating invalid form:")
    handleValidation(validateRegistration(invalidForm))
}
```

---

## Ответ

### Вопрос
Расскажи data классы и sealed классы.

### Ответ
Data классы в Kotlin предназначены для хранения данных и автоматически генерируют методы, такие как equals(), hashCode(), toString() и copy(). Они идеально подходят для создания POJO/POCO объектов. Sealed классы используются для представления ограниченного набора типов, похожих на перечисления, но с возможностью иметь классы с разными свойствами и методами. Это помогает обеспечить безопасное использование при работе с типами во время компиляции, улучшая обработку ошибок и логику ветвления.

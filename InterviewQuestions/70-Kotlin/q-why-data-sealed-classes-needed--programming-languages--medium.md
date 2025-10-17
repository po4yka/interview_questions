---
id: "20251015082237067"
title: "Why Data Sealed Classes Needed"
topic: kotlin
difficulty: medium
status: draft
created: 2025-10-15
tags: - programming-languages
---
# Why are Data Class and Sealed Classes needed?

**English**: Why are Data Class and Sealed Classes needed in Kotlin?

## Answer (EN)
**Data Class** are designed for storing data and automatically provide a number of useful methods, which simplifies development and reduces boilerplate code.

**Main reasons for using Data Class:**
1. **Code reduction** - Auto-generates `equals()`, `hashCode()`, `toString()`, `copy()`, and `componentN()`
2. **Simplified data transfer** - Perfect for DTOs and models
3. **Immutability support** - Encourages immutable data with `val` and `copy()`

**Sealed Class** are used to define closed class hierarchies where all descendants are known and limited.

**Main reasons for using Sealed Class:**
1. **Complete case coverage in `when`** - Compiler ensures all cases are handled
2. **Restricted inheritance** - All subclasses must be in the same file/module
3. **Encapsulation** - Represents a finite set of types

### Code Examples

**Data Class - Code Reduction:**

```kotlin
// WITHOUT data class - verbose
class PersonOld(val name: String, val age: Int, val email: String) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is PersonOld) return false
        return name == other.name && age == other.age && email == other.email
    }

    override fun hashCode(): Int {
        var result = name.hashCode()
        result = 31 * result + age
        result = 31 * result + email.hashCode()
        return result
    }

    override fun toString(): String {
        return "PersonOld(name='$name', age=$age, email='$email')"
    }

    fun copy(
        name: String = this.name,
        age: Int = this.age,
        email: String = this.email
    ): PersonOld {
        return PersonOld(name, age, email)
    }
}

// WITH data class - concise
data class Person(
    val name: String,
    val age: Int,
    val email: String
)

fun main() {
    val person = Person("Alice", 30, "alice@example.com")

    // All functionality automatically available
    println(person)  // toString()
    val older = person.copy(age = 31)  // copy()
    println(person == older)  // equals()

    // Destructuring
    val (name, age, email) = person
    println("$name is $age years old")
}
```

**Data Class - Simplified Data Transfer:**

```kotlin
// API Request/Response models
data class LoginRequest(
    val username: String,
    val password: String
)

data class LoginResponse(
    val success: Boolean,
    val token: String?,
    val userId: Int?,
    val message: String
)

// Database entity
data class UserEntity(
    val id: Long,
    val username: String,
    val email: String,
    val createdAt: Long,
    val updatedAt: Long
)

// DTO (Data Transfer Object)
data class UserDto(
    val username: String,
    val email: String
) {
    companion object {
        fun from(entity: UserEntity) = UserDto(
            username = entity.username,
            email = entity.email
        )
    }
}

fun simulateApiCall(request: LoginRequest): LoginResponse {
    return if (request.username == "admin" && request.password == "password") {
        LoginResponse(
            success = true,
            token = "abc123xyz",
            userId = 1,
            message = "Login successful"
        )
    } else {
        LoginResponse(
            success = false,
            token = null,
            userId = null,
            message = "Invalid credentials"
        )
    }
}

fun main() {
    val request = LoginRequest("admin", "password")
    val response = simulateApiCall(request)

    println("Login ${if (response.success) "successful" else "failed"}")
    println("Message: ${response.message}")

    val entity = UserEntity(1, "admin", "admin@example.com", 1000L, 1000L)
    val dto = UserDto.from(entity)
    println("DTO: $dto")
}
```

**Data Class - Immutability Support:**

```kotlin
// Immutable data class
data class Money(
    val amount: Double,
    val currency: String
) {
    init {
        require(amount >= 0) { "Amount cannot be negative" }
        require(currency.length == 3) { "Currency must be 3-letter code" }
    }

    // Operations return new instances
    fun add(other: Money): Money {
        require(currency == other.currency) { "Currency mismatch" }
        return copy(amount = amount + other.amount)
    }

    fun multiply(factor: Double): Money {
        return copy(amount = amount * factor)
    }
}

fun main() {
    val price = Money(100.0, "USD")
    val tax = Money(10.0, "USD")

    val total = price.add(tax)
    println("Original price: $price")  // Not modified
    println("Total: $total")

    val doubled = price.multiply(2.0)
    println("Doubled: $doubled")
}
```

**Sealed Class - Complete Case Coverage:**

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String, val code: Int) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Compiler ensures all cases are handled
fun <T> handleResult(result: Result<T>): String {
    return when (result) {
        is Result.Success -> "Success: ${result.data}"
        is Result.Error -> "Error ${result.code}: ${result.message}"
        Result.Loading -> "Loading..."
        // No else needed - compiler knows all possible types
    }
}

fun main() {
    val results = listOf<Result<String>>(
        Result.Success("Data loaded"),
        Result.Error("Not found", 404),
        Result.Loading
    )

    results.forEach { result ->
        println(handleResult(result))
    }
}
```

**Sealed Class - Restricted Inheritance:**

```kotlin
// All possible navigation destinations defined here
sealed class Screen {
    object Home : Screen()

    object Profile : Screen()

    data class UserDetails(val userId: Int) : Screen()

    data class ArticleView(val articleId: String, val source: String) : Screen()

    data class Settings(val section: String? = null) : Screen()
}

// Type-safe navigation
class Navigator {
    private val history = mutableListOf<Screen>()

    fun navigate(screen: Screen) {
        history.add(screen)
        when (screen) {
            Screen.Home -> println("Navigating to Home")
            Screen.Profile -> println("Navigating to Profile")
            is Screen.UserDetails -> println("Viewing user ${screen.userId}")
            is Screen.ArticleView -> println("Reading article ${screen.articleId}")
            is Screen.Settings -> {
                val section = screen.section ?: "general"
                println("Opening settings: $section")
            }
        }
    }

    fun back(): Screen? {
        return if (history.size > 1) {
            history.removeLast()
            history.last()
        } else {
            null
        }
    }
}

fun main() {
    val navigator = Navigator()

    navigator.navigate(Screen.Home)
    navigator.navigate(Screen.UserDetails(42))
    navigator.navigate(Screen.Settings("privacy"))

    navigator.back()
}
```

**Sealed Class - Encapsulation:**

```kotlin
// State machine with sealed class
sealed class OrderState {
    object Created : OrderState()

    data class PaymentPending(val amount: Double) : OrderState()

    data class Paid(val transactionId: String, val paidAt: Long) : OrderState()

    data class Shipped(val trackingNumber: String, val shippedAt: Long) : OrderState()

    data class Delivered(val deliveredAt: Long) : OrderState()

    data class Cancelled(val reason: String, val cancelledAt: Long) : OrderState()
}

data class Order(
    val id: String,
    val items: List<String>,
    val state: OrderState
) {
    fun transition(newState: OrderState): Order {
        // Validate state transitions
        val isValidTransition = when (state) {
            OrderState.Created -> newState is OrderState.PaymentPending || newState is OrderState.Cancelled
            is OrderState.PaymentPending -> newState is OrderState.Paid || newState is OrderState.Cancelled
            is OrderState.Paid -> newState is OrderState.Shipped || newState is OrderState.Cancelled
            is OrderState.Shipped -> newState is OrderState.Delivered
            is OrderState.Delivered -> false
            is OrderState.Cancelled -> false
        }

        require(isValidTransition) {
            "Cannot transition from $state to $newState"
        }

        return copy(state = newState)
    }
}

fun displayOrderStatus(order: Order) {
    val status = when (val state = order.state) {
        OrderState.Created -> "Order created, awaiting payment"
        is OrderState.PaymentPending -> "Payment pending: $${state.amount}"
        is OrderState.Paid -> "Paid (Transaction: ${state.transactionId})"
        is OrderState.Shipped -> "Shipped (Tracking: ${state.trackingNumber})"
        is OrderState.Delivered -> "Delivered"
        is OrderState.Cancelled -> "Cancelled: ${state.reason}"
    }

    println("Order ${order.id}: $status")
}

fun main() {
    var order = Order("ORD-001", listOf("Laptop", "Mouse"), OrderState.Created)
    displayOrderStatus(order)

    order = order.transition(OrderState.PaymentPending(1029.99))
    displayOrderStatus(order)

    order = order.transition(OrderState.Paid("TXN-123", System.currentTimeMillis()))
    displayOrderStatus(order)

    order = order.transition(OrderState.Shipped("TRACK-456", System.currentTimeMillis()))
    displayOrderStatus(order)

    // Invalid transition
    try {
        order = order.transition(OrderState.Created)
    } catch (e: IllegalArgumentException) {
        println("Error: ${e.message}")
    }
}
```

**Combined Power: Data Class + Sealed Class:**

```kotlin
// Domain models (data classes)
data class User(val id: Int, val name: String)
data class Post(val id: Int, val title: String, val content: String)

// Loading states (sealed class)
sealed class LoadingState<out T> {
    object Idle : LoadingState<Nothing>()
    object Loading : LoadingState<Nothing>()
    data class Success<T>(val data: T, val timestamp: Long) : LoadingState<T>()
    data class Error(val exception: Throwable) : LoadingState<Nothing>()
}

// Repository
class UserRepository {
    private var state: LoadingState<User> = LoadingState.Idle

    fun loadUser(id: Int): LoadingState<User> {
        state = LoadingState.Loading
        return try {
            // Simulate loading
            val user = User(id, "Alice")
            LoadingState.Success(user, System.currentTimeMillis()).also {
                state = it
            }
        } catch (e: Exception) {
            LoadingState.Error(e).also {
                state = it
            }
        }
    }

    fun getState() = state
}

// UI
fun renderUserProfile(state: LoadingState<User>) {
    when (state) {
        LoadingState.Idle -> {
            println("No user loaded yet")
        }
        LoadingState.Loading -> {
            println("Loading user profile...")
        }
        is LoadingState.Success -> {
            val user = state.data
            println("User Profile:")
            println("  ID: ${user.id}")
            println("  Name: ${user.name}")
            println("  Loaded at: ${state.timestamp}")
        }
        is LoadingState.Error -> {
            println("Failed to load user: ${state.exception.message}")
        }
    }
}

fun main() {
    val repository = UserRepository()

    renderUserProfile(repository.getState())  // Idle

    val result = repository.loadUser(1)
    renderUserProfile(result)  // Success
}
```

---

## Ответ (RU)
# Вопрос (RU)
Зачем нужны Data Class и Sealed Classes?

## Ответ (RU)
Data Class предназначены для хранения данных и автоматически предоставляют ряд полезных методов, что упрощает разработку и уменьшает объем шаблонного кода. Основные причины использования Data Class: Сокращение кода, Упрощение передачи данных и Поддержка неизменяемости. Sealed Class используются для определения закрытых иерархий классов, где все потомки известны и ограничены. Они полезны по следующим причинам: Полное покрытие случаев в `when`, Ограниченное наследование и Инкапсуляция.

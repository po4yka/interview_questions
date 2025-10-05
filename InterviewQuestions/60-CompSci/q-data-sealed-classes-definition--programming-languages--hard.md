---
tags:
  - programming-languages
difficulty: hard
---

# What are Data Class and Sealed Classes?

**English**: What are Data Class and Sealed Classes in Kotlin?

## Answer

**Data Class:**
A special type of class designed for storing data. The main purpose is to hold data without performing any additional logic. Declared using the `data` keyword.

**Key features of data class:**
- **Automatic method generation**: Kotlin automatically generates `equals()`, `hashCode()`, and `toString()`, as well as `copy()` and component functions (`componentN()`)
- **Usage**: Widely used for data transfer between program components, in MVC or MVVM models, in DTOs (Data Transfer Objects) and POJOs (Plain Old Java Objects)
- **Requirements**: Must have at least one parameter in primary constructor, all parameters must be `val` or `var`

**Sealed Class:**
A class that restricts inheritance. It allows defining limited class hierarchies where all possible subclasses are known at compile time. Particularly useful with the `when` pattern, as the compiler can verify that all possible cases are handled.

**Key features:**
- **Restricted inheritance**: All subclasses must be declared in the same file as the sealed class (or same module in Kotlin 1.5+)
- **Usage with `when`**: Perfect for use in `when` expressions, since Kotlin knows all possible subclasses and can guarantee all cases are handled
- **Type safety**: Provides compile-time safety for representing a finite set of types

### Code Examples

**Data Class comprehensive example:**

```kotlin
// Basic data class
data class Product(
    val id: Int,
    val name: String,
    val price: Double,
    val category: String
)

fun main() {
    val laptop = Product(1, "MacBook Pro", 2499.99, "Electronics")

    // 1. Automatic toString()
    println(laptop)
    // Product(id=1, name=MacBook Pro, price=2499.99, category=Electronics)

    // 2. Automatic equals() - content comparison
    val laptop2 = Product(1, "MacBook Pro", 2499.99, "Electronics")
    println(laptop == laptop2)  // true

    // 3. Automatic hashCode() - works in hash collections
    val productSet = setOf(laptop, laptop2)
    println("Set size: ${productSet.size}")  // 1 (duplicates removed)

    val productMap = mapOf(laptop to "In Stock")
    println(productMap[laptop2])  // "In Stock" (found by content)

    // 4. copy() method - create modified copies
    val discountedLaptop = laptop.copy(price = 1999.99)
    println(discountedLaptop)
    // Product(id=1, name=MacBook Pro, price=1999.99, category=Electronics)

    // 5. Destructuring with componentN()
    val (id, name, price, category) = laptop
    println("$name costs $$price")  // MacBook Pro costs $2499.99
}
```

**Data class in MVC/MVVM:**

```kotlin
// Model layer
data class User(
    val id: Int,
    val username: String,
    val email: String,
    val firstName: String,
    val lastName: String,
    val isActive: Boolean
) {
    // Additional methods can be added
    fun getFullName() = "$firstName $lastName"
}

// DTO for API
data class CreateUserRequest(
    val username: String,
    val email: String,
    val password: String,
    val firstName: String,
    val lastName: String
)

data class UserResponse(
    val success: Boolean,
    val user: User?,
    val message: String
)

// ViewModel
class UserViewModel {
    private var currentUser: User? = null

    fun createUser(request: CreateUserRequest): UserResponse {
        // Simulate user creation
        val newUser = User(
            id = 1,
            username = request.username,
            email = request.email,
            firstName = request.firstName,
            lastName = request.lastName,
            isActive = true
        )
        currentUser = newUser

        return UserResponse(
            success = true,
            user = newUser,
            message = "User created successfully"
        )
    }

    fun updateUserEmail(newEmail: String): User? {
        currentUser = currentUser?.copy(email = newEmail)
        return currentUser
    }
}

fun main() {
    val viewModel = UserViewModel()

    val request = CreateUserRequest(
        username = "alice",
        email = "alice@example.com",
        password = "secret123",
        firstName = "Alice",
        lastName = "Johnson"
    )

    val response = viewModel.createUser(request)
    println("Success: ${response.success}")
    println("User: ${response.user?.getFullName()}")

    val updated = viewModel.updateUserEmail("alice.johnson@example.com")
    println("Updated email: ${updated?.email}")
}
```

**Sealed Class comprehensive example:**

```kotlin
// Sealed class hierarchy
sealed class Shape {
    data class Circle(val radius: Double) : Shape()
    data class Rectangle(val width: Double, val height: Double) : Shape()
    data class Triangle(val base: Double, val height: Double) : Shape()
    object Unknown : Shape()
}

// Calculate area - compiler ensures all cases are covered
fun calculateArea(shape: Shape): Double {
    return when (shape) {
        is Shape.Circle -> Math.PI * shape.radius * shape.radius
        is Shape.Rectangle -> shape.width * shape.height
        is Shape.Triangle -> 0.5 * shape.base * shape.height
        Shape.Unknown -> 0.0
        // No 'else' needed - compiler knows all subclasses
    }
}

// Calculate perimeter
fun calculatePerimeter(shape: Shape): Double {
    return when (shape) {
        is Shape.Circle -> 2 * Math.PI * shape.radius
        is Shape.Rectangle -> 2 * (shape.width + shape.height)
        is Shape.Triangle -> {
            // Approximate for equilateral triangle
            3 * shape.base
        }
        Shape.Unknown -> 0.0
    }
}

fun main() {
    val shapes = listOf(
        Shape.Circle(5.0),
        Shape.Rectangle(4.0, 6.0),
        Shape.Triangle(3.0, 4.0),
        Shape.Unknown
    )

    shapes.forEach { shape ->
        println("Shape: $shape")
        println("Area: ${calculateArea(shape)}")
        println("Perimeter: ${calculatePerimeter(shape)}")
        println()
    }
}
```

**Sealed class with `when` expression:**

```kotlin
// Navigation state
sealed class Screen {
    object Home : Screen()
    object Profile : Screen()
    data class UserDetails(val userId: Int) : Screen()
    data class Settings(val section: String) : Screen()
    object Login : Screen()
}

// Type-safe navigation
fun navigate(screen: Screen) {
    when (screen) {
        Screen.Home -> println("Navigating to Home screen")
        Screen.Profile -> println("Navigating to Profile screen")
        is Screen.UserDetails -> {
            println("Navigating to User Details for user ${screen.userId}")
        }
        is Screen.Settings -> {
            println("Navigating to Settings: ${screen.section}")
        }
        Screen.Login -> println("Navigating to Login screen")
        // Compiler error if any case is missing!
    }
}

fun main() {
    navigate(Screen.Home)
    navigate(Screen.UserDetails(42))
    navigate(Screen.Settings("Privacy"))
}
```

**Advanced: Sealed class for API responses:**

```kotlin
// Generic sealed class for API results
sealed class ApiResponse<out T> {
    data class Success<T>(
        val data: T,
        val statusCode: Int = 200,
        val headers: Map<String, String> = emptyMap()
    ) : ApiResponse<T>()

    data class Error(
        val statusCode: Int,
        val message: String,
        val errors: List<String> = emptyList()
    ) : ApiResponse<Nothing>()

    object Loading : ApiResponse<Nothing>()

    object NotAuthenticated : ApiResponse<Nothing>()
}

// Domain models
data class Article(
    val id: Int,
    val title: String,
    val content: String,
    val author: String,
    val publishedAt: Long
)

// API service
class ArticleService {
    fun fetchArticles(): ApiResponse<List<Article>> {
        return try {
            val articles = listOf(
                Article(1, "Kotlin Basics", "Learn Kotlin...", "Alice", System.currentTimeMillis()),
                Article(2, "Advanced Kotlin", "Deep dive...", "Bob", System.currentTimeMillis())
            )
            ApiResponse.Success(
                data = articles,
                statusCode = 200,
                headers = mapOf("Content-Type" to "application/json")
            )
        } catch (e: Exception) {
            ApiResponse.Error(500, "Server error", listOf(e.message ?: "Unknown error"))
        }
    }
}

// UI handler
fun displayArticles(response: ApiResponse<List<Article>>) {
    when (response) {
        is ApiResponse.Success -> {
            println("Success! Status: ${response.statusCode}")
            response.data.forEach { article ->
                println("${article.title} by ${article.author}")
            }
        }
        is ApiResponse.Error -> {
            println("Error ${response.statusCode}: ${response.message}")
            response.errors.forEach { println("  - $it") }
        }
        ApiResponse.Loading -> {
            println("Loading articles...")
        }
        ApiResponse.NotAuthenticated -> {
            println("Please log in to view articles")
        }
    }
}

fun main() {
    val service = ArticleService()
    val response = service.fetchArticles()
    displayArticles(response)
}
```

**Combining Data Class and Sealed Class:**

```kotlin
// State management example
data class FormData(
    val username: String = "",
    val email: String = "",
    val password: String = ""
)

sealed class FormState {
    object Initial : FormState()
    data class Editing(val data: FormData) : FormState()
    data class Validating(val data: FormData) : FormState()
    data class Valid(val data: FormData) : FormState()
    data class Invalid(val data: FormData, val errors: List<String>) : FormState()
    data class Submitting(val data: FormData) : FormState()
    data class Submitted(val data: FormData, val userId: Int) : FormState()
}

fun validateForm(data: FormData): FormState {
    val errors = mutableListOf<String>()

    if (data.username.length < 3) {
        errors.add("Username must be at least 3 characters")
    }
    if (!data.email.contains("@")) {
        errors.add("Invalid email address")
    }
    if (data.password.length < 8) {
        errors.add("Password must be at least 8 characters")
    }

    return if (errors.isEmpty()) {
        FormState.Valid(data)
    } else {
        FormState.Invalid(data, errors)
    }
}

fun handleFormState(state: FormState) {
    when (state) {
        FormState.Initial -> {
            println("Form is ready for input")
        }
        is FormState.Editing -> {
            println("Editing form: ${state.data.username}")
        }
        is FormState.Validating -> {
            println("Validating form...")
        }
        is FormState.Valid -> {
            println("Form is valid! Ready to submit")
        }
        is FormState.Invalid -> {
            println("Form has errors:")
            state.errors.forEach { println("  - $it") }
        }
        is FormState.Submitting -> {
            println("Submitting form for ${state.data.username}...")
        }
        is FormState.Submitted -> {
            println("Form submitted! User ID: ${state.userId}")
        }
    }
}

fun main() {
    val formData = FormData(
        username = "al",
        email = "invalid-email",
        password = "123"
    )

    val validationResult = validateForm(formData)
    handleFormState(validationResult)

    println()

    val validFormData = FormData(
        username = "alice",
        email = "alice@example.com",
        password = "securepass123"
    )

    val validResult = validateForm(validFormData)
    handleFormState(validResult)
}
```

---

## Ответ

### Вопрос
Что такое Data Class и Sealed Classes

### Ответ
Data Class — Это специальный тип класса, предназначенный для хранения данных. Основная цель таких классов — содержать данные и не выполнять никакой дополнительной логики. Для объявления используется ключевое слово data. Особенности data class: Автоматическая генерация методов: Kotlin автоматически генерирует методы equals(), hashCode(), и toString(), а также copy() и компонентные функции (componentN()), которые облегчают работу с объектами. Использование: Data class широко используется для передачи данных между компонентами программы, в моделях MVC или MVVM, в DTO (Data Transfer Objects) и POJO (Plain Old Java Object) в Java-экосистеме. Sealed Class Это класс, который ограничивает возможность наследования. Другими словами, такие классы позволяют определять ограниченные иерархии классов, где все возможные подклассы известны во время компиляции. Это особенно полезно в сочетании с паттерном when, так как компилятор может проверить, обработаны ли все возможные случаи. Особенности: Ограниченное наследование: Все подклассы данного класса должны быть объявлены в том же файле, что и sealed класс. Использование с `when`: Идеально подходят для использования в выражениях when, поскольку Kotlin знает все возможные подклассы и может гарантировать, что все случаи обработаны.

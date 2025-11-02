---
id: kotlin-212
title: "Data Sealed Classes Definition / Data и Sealed классы определение"
aliases: [Data Sealed Classes, Data и Sealed классы]
topic: kotlin
subtopics: [data-classes, sealed-classes]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-kotlin-channels--kotlin--medium, q-kotlin-sam-conversions--programming-languages--medium, q-sequences-vs-collections-performance--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [data-classes, difficulty/hard, programming-languages, sealed-classes]
date created: Friday, October 31st 2025, 6:33:11 pm
date modified: Saturday, November 1st 2025, 5:43:22 pm
---

# What Are Data Class and Sealed Classes?

# Question (EN)
> What are Data Class and Sealed Classes in Kotlin? Explain their characteristics, use cases, and provide comprehensive examples.

# Вопрос (RU)
> Что такое Data Class и Sealed Classes в Kotlin? Объясните их характеристики, применения и приведите подробные примеры.

---

## Answer (EN)

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

## Ответ (RU)

### Data Class

**Data Class** — специальный тип класса, предназначенный для хранения данных. Основная цель — содержать данные без выполнения дополнительной логики. Объявляется с ключевым словом `data`.

**Ключевые особенности data class:**

1. **Автоматическая генерация методов**: Kotlin автоматически генерирует:
   - `equals()` — сравнение по содержимому
   - `hashCode()` — для hash-коллекций
   - `toString()` — строковое представление
   - `copy()` — создание копий с изменениями
   - `componentN()` — компонентные функции для деструктуризации

2. **Использование**:
   - Передача данных между компонентами программы
   - Модели в MVC или MVVM
   - DTO (Data Transfer Objects)
   - POJO (Plain Old Java Objects)

3. **Требования**:
   - Минимум один параметр в primary constructor
   - Все параметры должны быть `val` или `var`

**Пример data class:**
```kotlin
data class Product(
    val id: Int,
    val name: String,
    val price: Double,
    val category: String
)

val laptop = Product(1, "MacBook Pro", 2499.99, "Electronics")

// Автоматический toString()
println(laptop)
// Product(id=1, name=MacBook Pro, price=2499.99, category=Electronics)

// Автоматический equals() - сравнение по содержимому
val laptop2 = Product(1, "MacBook Pro", 2499.99, "Electronics")
println(laptop == laptop2)  // true

// Автоматический hashCode() - работает в hash-коллекциях
val productSet = setOf(laptop, laptop2)
println("Set size: ${productSet.size}")  // 1 (дубликаты удалены)

// copy() метод - создание изменённых копий
val discountedLaptop = laptop.copy(price = 1999.99)
println(discountedLaptop)
// Product(id=1, name=MacBook Pro, price=1999.99, category=Electronics)

// Деструктуризация с componentN()
val (id, name, price, category) = laptop
println("$name стоит $$price")  // MacBook Pro стоит $2499.99
```

**Data class в MVC/MVVM:**
```kotlin
// Model слой
data class User(
    val id: Int,
    val username: String,
    val email: String,
    val firstName: String,
    val lastName: String,
    val isActive: Boolean
) {
    // Дополнительные методы можно добавлять
    fun getFullName() = "$firstName $lastName"
}

// DTO для API
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
            message = "Пользователь создан успешно"
        )
    }

    fun updateUserEmail(newEmail: String): User? {
        currentUser = currentUser?.copy(email = newEmail)
        return currentUser
    }
}
```

### Sealed Class

**Sealed Class** — класс, который ограничивает наследование. Позволяет определять ограниченные иерархии классов, где все возможные подклассы известны во время компиляции. Особенно полезен с паттерном `when`, так как компилятор может проверить, что все случаи обработаны.

**Ключевые особенности:**

1. **Ограниченное наследование**: Все подклассы должны быть объявлены в том же файле, что и sealed класс (или в том же модуле в Kotlin 1.5+)

2. **Использование с `when`**: Идеально подходят для `when` выражений, поскольку Kotlin знает все возможные подклассы и может гарантировать exhaustive checking

3. **Типобезопасность**: Обеспечивает compile-time безопасность для представления конечного набора типов

**Пример sealed class:**
```kotlin
// Sealed class иерархия
sealed class Shape {
    data class Circle(val radius: Double) : Shape()
    data class Rectangle(val width: Double, val height: Double) : Shape()
    data class Triangle(val base: Double, val height: Double) : Shape()
    object Unknown : Shape()
}

// Расчёт площади - компилятор проверяет все случаи
fun calculateArea(shape: Shape): Double {
    return when (shape) {
        is Shape.Circle -> Math.PI * shape.radius * shape.radius
        is Shape.Rectangle -> shape.width * shape.height
        is Shape.Triangle -> 0.5 * shape.base * shape.height
        Shape.Unknown -> 0.0
        // else не нужен - компилятор знает все подклассы
    }
}

val shapes = listOf(
    Shape.Circle(5.0),
    Shape.Rectangle(4.0, 6.0),
    Shape.Triangle(3.0, 4.0),
    Shape.Unknown
)

shapes.forEach { shape ->
    println("Фигура: $shape")
    println("Площадь: ${calculateArea(shape)}")
}
```

**Sealed class для навигации:**
```kotlin
sealed class Screen {
    object Home : Screen()
    object Profile : Screen()
    data class UserDetails(val userId: Int) : Screen()
    data class Settings(val section: String) : Screen()
    object Login : Screen()
}

// Типобезопасная навигация
fun navigate(screen: Screen) {
    when (screen) {
        Screen.Home -> println("Навигация на главный экран")
        Screen.Profile -> println("Навигация на профиль")
        is Screen.UserDetails -> {
            println("Навигация к пользователю ${screen.userId}")
        }
        is Screen.Settings -> {
            println("Навигация в настройки: ${screen.section}")
        }
        Screen.Login -> println("Навигация на вход")
        // Ошибка компиляции если пропущен случай!
    }
}
```

**Продвинутый пример: Sealed class для API ответов:**
```kotlin
// Универсальный sealed class для API результатов
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

// Domain модели
data class Article(
    val id: Int,
    val title: String,
    val content: String,
    val author: String,
    val publishedAt: Long
)

// API сервис
class ArticleService {
    fun fetchArticles(): ApiResponse<List<Article>> {
        return try {
            val articles = listOf(
                Article(1, "Основы Kotlin", "Изучаем Kotlin...", "Алиса", System.currentTimeMillis()),
                Article(2, "Продвинутый Kotlin", "Глубокое погружение...", "Боб", System.currentTimeMillis())
            )
            ApiResponse.Success(
                data = articles,
                statusCode = 200,
                headers = mapOf("Content-Type" to "application/json")
            )
        } catch (e: Exception) {
            ApiResponse.Error(500, "Ошибка сервера", listOf(e.message ?: "Неизвестная ошибка"))
        }
    }
}

// UI обработчик
fun displayArticles(response: ApiResponse<List<Article>>) {
    when (response) {
        is ApiResponse.Success -> {
            println("Успешно! Статус: ${response.statusCode}")
            response.data.forEach { article ->
                println("${article.title} от ${article.author}")
            }
        }
        is ApiResponse.Error -> {
            println("Ошибка ${response.statusCode}: ${response.message}")
            response.errors.forEach { println("  - $it") }
        }
        ApiResponse.Loading -> {
            println("Загрузка статей...")
        }
        ApiResponse.NotAuthenticated -> {
            println("Войдите чтобы просмотреть статьи")
        }
    }
}
```

### Комбинирование Data Class И Sealed Class

**Очень распространённый паттерн - sealed class с data подклассами:**
```kotlin
// Управление состоянием формы
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
        errors.add("Имя пользователя должно быть не менее 3 символов")
    }
    if (!data.email.contains("@")) {
        errors.add("Неверный email адрес")
    }
    if (data.password.length < 8) {
        errors.add("Пароль должен быть не менее 8 символов")
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
            println("Форма готова к вводу")
        }
        is FormState.Editing -> {
            println("Редактирование формы: ${state.data.username}")
        }
        is FormState.Validating -> {
            println("Валидация формы...")
        }
        is FormState.Valid -> {
            println("Форма валидна! Готова к отправке")
        }
        is FormState.Invalid -> {
            println("Ошибки в форме:")
            state.errors.forEach { println("  - $it") }
        }
        is FormState.Submitting -> {
            println("Отправка формы для ${state.data.username}...")
        }
        is FormState.Submitted -> {
            println("Форма отправлена! ID пользователя: ${state.userId}")
        }
    }
}
```

### Сравнительная Таблица

| Характеристика | Data Class | Sealed Class |
|----------------|-----------|--------------|
| **Назначение** | Хранение данных | Ограниченная иерархия типов |
| **Автогенерация** | equals, hashCode, toString, copy, componentN | Нет |
| **Наследование** | Может быть final или open | Всегда open для подклассов |
| **Подклассы** | Не ограничены | Ограничены файлом/модулем |
| **Применение** | Модели, DTOs, POJOs | Состояния, результаты, события |
| **When exhaustive** | Нет | Да |
| **Деструктуризация** | Да (componentN) | Нет (только у data подклассов) |
| **copy()** | Да | Нет (только у data подклассов) |

### Краткий Ответ

**Data Class**: Специальный класс для хранения данных. Автоматически генерирует `equals()`, `hashCode()`, `toString()`, `copy()` и `componentN()`. Требования: минимум один параметр в primary constructor, все параметры `val`/`var`. Используется для моделей данных, DTOs, API responses, MVC/MVVM моделей.

**Sealed Class**: Ограничивает наследование одним файлом/модулем. Создаёт типобезопасные иерархии с exhaustive when-проверками. Все подклассы известны на этапе компиляции. Используется для UI состояний (Loading/Success/Error), Result типов, навигационных событий, command паттернов.

**Комбинирование**: Очень распространён паттерн sealed класса с data подклассами для управления состояниями с данными (например, `sealed class UiState` с `data class Success(val data: T)`).

## Related Questions

- [[q-kotlin-sam-conversions--programming-languages--medium]]
- [[q-sequences-vs-collections-performance--kotlin--medium]]
- [[q-kotlin-channels--kotlin--medium]]

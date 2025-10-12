---
tags:
  - programming-languages
difficulty: medium
status: draft
---

# What is known about data classes and sealed classes?

# Question (EN)
> What is known about data classes and sealed classes in Kotlin? What are their characteristics and use cases?

# Вопрос (RU)
> Что известно о data классах и sealed классах в Kotlin? Каковы их характеристики и применения?

---

## Answer (EN)

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

## Ответ (RU)

### Data классы

**Data классы** предназначены для хранения данных и автоматически генерируют несколько полезных методов:
- `equals()` - для сравнения по содержимому
- `hashCode()` - для использования в hash-коллекциях
- `toString()` - для строкового представления
- `copy()` - для создания копий с изменёнными свойствами
- `componentN()` - компонентные функции для деструктуризации

**Применение:**
- Модели данных в приложениях
- DTO (Data Transfer Objects)
- POJO (Plain Old Java Objects)
- API response models

**Пример:**
```kotlin
data class User(
    val id: Int,
    val name: String,
    val email: String,
    val age: Int
)

val user1 = User(1, "Alice", "alice@example.com", 30)
val user2 = User(1, "Alice", "alice@example.com", 30)

// Автоматический equals()
println(user1 == user2)  // true (одинаковое содержимое)

// Автоматический toString()
println(user1)  // User(id=1, name=Alice, email=alice@example.com, age=30)

// copy() функция
val olderUser = user1.copy(age = 31)

// Деструктуризация с componentN()
val (id, name, email, age) = user1
println("$name is $age years old")
```

### Sealed классы

**Sealed классы** ограничивают создание подклассов тем же файлом (или модулем в Kotlin 1.5+) и используются для создания типобезопасных иерархий:
- Все возможные подклассы известны на этапе компиляции
- Идеальны для представления ограниченных иерархий классов
- Отлично работают с `when` выражениями (exhaustive checking)
- Часто используются для управления состояниями в архитектурных компонентах

**Применение:**
- Управление UI состояниями (Loading, Success, Error)
- Result/Response типы для сетевых запросов
- Навигационные события
- Sealed иерархии команд или действий

**Пример UI состояния:**
```kotlin
sealed class UiState {
    object Loading : UiState()
    data class Success(val data: List<String>) : UiState()
    data class Error(val message: String, val code: Int) : UiState()
    object Empty : UiState()
}

fun renderUi(state: UiState) {
    when (state) {
        is UiState.Loading -> println("Показываем загрузку...")
        is UiState.Success -> println("Отображаем данные: ${state.data}")
        is UiState.Error -> println("Ошибка ${state.code}: ${state.message}")
        is UiState.Empty -> println("Нет данных")
        // else не нужен - компилятор знает все варианты
    }
}
```

**Пример сетевого результата:**
```kotlin
sealed class NetworkResult<out T> {
    data class Success<T>(val data: T) : NetworkResult<T>()
    data class Error(val exception: Exception) : NetworkResult<Nothing>()
    object Loading : NetworkResult<Nothing>()
}

data class Product(val id: Int, val name: String, val price: Double)

fun fetchProducts(): NetworkResult<List<Product>> {
    return try {
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
            println("Загружено ${result.data.size} товаров:")
            result.data.forEach { product ->
                println("  ${product.name}: $${product.price}")
            }
        }
        is NetworkResult.Error -> {
            println("Ошибка: ${result.exception.message}")
        }
        NetworkResult.Loading -> {
            println("Загрузка товаров...")
        }
    }
}
```

### Комбинирование data и sealed классов

**Очень распространённый паттерн - sealed класс с data подклассами:**
```kotlin
sealed class Result {
    data class Success(val value: Int) : Result()
    data class Failure(val error: String) : Result()
}

fun divide(a: Int, b: Int): Result {
    return if (b != 0) {
        Result.Success(a / b)
    } else {
        Result.Failure("Деление на ноль")
    }
}

val result1 = divide(10, 2)
when (result1) {
    is Result.Success -> println("Результат: ${result1.value}")
    is Result.Failure -> println("Ошибка: ${result1.error}")
}
```

### Android MVVM пример

**Типичное использование в Android с ViewModel:**
```kotlin
// Data класс для данных профиля
data class UserProfile(
    val name: String,
    val email: String,
    val avatarUrl: String
)

// Sealed класс для состояний
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
        // Симуляция загрузки
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

// В Activity/Fragment
when (val state = viewModel.getState()) {
    is ProfileState.Initial -> println("Ещё не загружено")
    is ProfileState.Loading -> println("Загрузка...")
    is ProfileState.Success -> {
        // Деструктуризация data класса
        val (name, email, avatarUrl) = state.profile
        println("Пользователь: $name, Email: $email")
    }
    is ProfileState.Error -> println("Ошибка: ${state.message}")
}
```

### Ключевые различия

| Характеристика | Data класс | Sealed класс |
|----------------|-----------|--------------|
| **Назначение** | Хранение данных | Ограниченная иерархия типов |
| **Автогенерация** | equals, hashCode, toString, copy, componentN | Нет |
| **Наследование** | Может быть final или open | Всегда open для подклассов |
| **Подклассы** | Не ограничены | Ограничены файлом/модулем |
| **Применение** | Модели, DTOs | Состояния, результаты, события |
| **When exhaustive** | Нет | Да |

### Краткий ответ

**Data классы**: Предназначены для хранения данных. Автоматически генерируют `equals()`, `hashCode()`, `toString()`, `copy()` и `componentN()`. Используются для моделей данных, DTOs, API responses.

**Sealed классы**: Ограничивают подклассы одним файлом/модулем. Создают типобезопасные иерархии с exhaustive when-проверками. Используются для UI состояний (Loading/Success/Error), Result типов, навигационных событий.

**В Android**: Data классы - для моделей данных, sealed классы - для управления состояниями в ViewModel. Часто комбинируются: sealed класс с data подклассами.

---
id: kotlin-204
title: "Data Sealed Difference / Разница data и sealed"
aliases: [Data vs Sealed Classes, Разница data и sealed]
topic: kotlin
subtopics: [data-classes, sealed-classes]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-value-classes-inline-classes--kotlin--medium, q-coroutine-parent-child-relationship--kotlin--medium, q-testing-viewmodel-coroutines--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags:
  - programming-languages
  - data-classes
  - sealed-classes
  - difficulty/medium
---
# What is the difference between data classes and sealed classes?

# Question (EN)
> What is the difference between data classes and sealed classes in Kotlin?

# Вопрос (RU)
> В чём разница между data class и sealed class в Kotlin?

---

## Answer (EN)

**data class** — A class for storing data with auto-generation of `equals()`, `hashCode()`, `copy()`.

**sealed class** — A restricted class hierarchy, used with `when` expressions.

**Key differences:**
- `data class` automatically creates `equals()`, `hashCode()`, `copy()`, `toString()`
- `sealed class` is used when there is a fixed number of subclasses
- `data class` is for data containers
- `sealed class` is for type hierarchies and state representation

### Code Examples

**data class - for data:**

```kotlin
// Data class - stores data
data class User(
    val id: Int,
    val name: String,
    val email: String
)

fun main() {
    val user1 = User(1, "Alice", "alice@example.com")
    val user2 = User(1, "Alice", "alice@example.com")

    // Auto-generated equals
    println(user1 == user2)  // true

    // Auto-generated toString
    println(user1)  // User(id=1, name=Alice, email=alice@example.com)

    // Auto-generated copy
    val user3 = user1.copy(email = "newemail@example.com")
    println(user3)

    // Auto-generated hashCode
    val users = setOf(user1, user2)
    println("Unique users: ${users.size}")  // 1
}
```

**sealed class - for hierarchies:**

```kotlin
// Sealed class - represents a type hierarchy
sealed class Result {
    data class Success(val value: Int) : Result()
    data class Error(val message: String) : Result()
    object Loading : Result()
}

fun handleResult(result: Result): String {
    // Exhaustive when - compiler knows all types
    return when (result) {
        is Result.Success -> "Value: ${result.value}"
        is Result.Error -> "Error: ${result.message}"
        Result.Loading -> "Loading..."
        // No else needed!
    }
}

fun main() {
    val results = listOf(
        Result.Success(42),
        Result.Error("Not found"),
        Result.Loading
    )

    results.forEach { result ->
        println(handleResult(result))
    }
}
```

**Comparison table:**

```kotlin
// DATA CLASS
data class Product(val id: Int, val name: String, val price: Double)

// Purpose: Store data
// Auto-generated: equals, hashCode, toString, copy, componentN
// Cannot be: abstract, open, sealed, inner
// Use case: DTOs, models, value objects

fun demonstrateDataClass() {
    val p1 = Product(1, "Laptop", 999.99)
    val p2 = p1.copy(price = 899.99)

    println(p1)  // toString
    println(p1 == p2)  // equals
    println(p1.hashCode())  // hashCode

    val (id, name, price) = p1  // componentN
}

// SEALED CLASS
sealed class State {
    object Loading : State()
    data class Success(val data: String) : State()
    data class Error(val code: Int) : State()
}

// Purpose: Restricted type hierarchy
// Auto-generated: Nothing
// Can be: abstract (implicitly)
// Use case: State management, result types, finite sets of types

fun demonstrateSealedClass(state: State) {
    when (state) {  // Exhaustive
        State.Loading -> println("Loading...")
        is State.Success -> println("Data: ${state.data}")
        is State.Error -> println("Error: ${state.code}")
    }
}
```

**When to use each:**

```kotlin
// Use DATA CLASS for:

// 1. API responses
data class ApiResponse(
    val success: Boolean,
    val data: String?,
    val error: String?
)

// 2. Database entities
data class UserEntity(
    val id: Long,
    val username: String,
    val email: String
)

// 3. Configuration
data class AppConfig(
    val apiUrl: String,
    val timeout: Int,
    val debugMode: Boolean
)

// Use SEALED CLASS for:

// 1. UI states
sealed class UiState {
    object Loading : UiState()
    data class Content(val items: List<String>) : UiState()
    data class Error(val message: String) : UiState()
}

// 2. Navigation
sealed class Screen {
    object Home : Screen()
    data class Details(val id: Int) : Screen()
    object Settings : Screen()
}

// 3. Network results
sealed class NetworkResult<out T> {
    data class Success<T>(val data: T) : NetworkResult<T>()
    data class Failure(val error: Throwable) : NetworkResult<Nothing>()
}
```

**Combining both:**

```kotlin
// Sealed class with data class subclasses
sealed class PaymentMethod {
    data class CreditCard(
        val number: String,
        val cvv: String,
        val expiry: String
    ) : PaymentMethod()

    data class PayPal(
        val email: String
    ) : PaymentMethod()

    object Cash : PaymentMethod()
}

fun processPayment(method: PaymentMethod, amount: Double) {
    when (method) {
        is PaymentMethod.CreditCard -> {
            // Data class provides all benefits
            val (number, cvv, expiry) = method
            println("Charging $$amount to card ending in ${number.takeLast(4)}")
        }
        is PaymentMethod.PayPal -> {
            println("Charging $$amount to PayPal account ${method.email}")
        }
        PaymentMethod.Cash -> {
            println("Processing cash payment of $$amount")
        }
    }
}

fun main() {
    val payment1 = PaymentMethod.CreditCard("1234567890123456", "123", "12/25")
    val payment2 = PaymentMethod.PayPal("user@example.com")
    val payment3 = PaymentMethod.Cash

    processPayment(payment1, 99.99)
    processPayment(payment2, 49.99)
    processPayment(payment3, 29.99)
}
```

**Real-world example:**

```kotlin
// Data classes for models
data class User(val id: Int, val name: String)
data class Post(val id: Int, val title: String, val content: String)
data class Comment(val id: Int, val text: String, val userId: Int)

// Sealed class for loading states
sealed class LoadingState<out T> {
    object Idle : LoadingState<Nothing>()
    object Loading : LoadingState<Nothing>()
    data class Success<T>(val data: T) : LoadingState<T>()
    data class Error(val exception: Throwable) : LoadingState<Nothing>()
}

// Usage
fun fetchUser(id: Int): LoadingState<User> {
    return try {
        val user = User(id, "Alice")  // data class
        LoadingState.Success(user)     // sealed class
    } catch (e: Exception) {
        LoadingState.Error(e)
    }
}

fun displayUserState(state: LoadingState<User>) {
    when (state) {
        LoadingState.Idle -> println("Not loaded")
        LoadingState.Loading -> println("Loading user...")
        is LoadingState.Success -> {
            val user = state.data
            println("User: ${user.name} (ID: ${user.id})")
        }
        is LoadingState.Error -> {
            println("Error: ${state.exception.message}")
        }
    }
}

fun main() {
    val state = fetchUser(1)
    displayUserState(state)
}
```

**Summary of differences:**

```kotlin
/*
DATA CLASS:
- Purpose: Data containers
- Auto-generates: equals, hashCode, toString, copy, componentN
- Cannot be: abstract, open, sealed, inner
- Use for: DTOs, models, API responses, entities

SEALED CLASS:
- Purpose: Type hierarchies
- Auto-generates: Nothing (but subclasses can be data classes)
- Cannot be: instantiated directly
- Use for: States, results, finite type sets, when expressions

KEY DIFFERENCE:
- Data class = "What data does this contain?"
- Sealed class = "What are all possible types?"
*/
```

---

## Ответ (RU)

**data class** — класс для хранения данных с автогенерацией `equals()`, `hashCode()`, `copy()`, `toString()`.

**sealed class** — ограниченная иерархия классов, используется с `when` выражениями для exhaustive проверок.

**Ключевые отличия:**

| Аспект | data class | sealed class |
|--------|-----------|--------------|
| **Назначение** | Хранение данных | Представление типов/состояний |
| **Автогенерация** | equals, hashCode, toString, copy, componentN | Ничего |
| **Наследование** | Не может быть abstract/open/sealed | Абстрактный по умолчанию |
| **Подклассы** | Нет подклассов | Фиксированный набор подклассов |
| **Use case** | DTO, модели, значения | Состояния, результаты, when |

### Примеры

**data class - для данных:**
```kotlin
data class User(val id: Int, val name: String, val email: String)

val user1 = User(1, "Alice", "alice@example.com")
val user2 = user1.copy(email = "new@example.com")
println(user1 == user2)  // false (auto-generated equals)
println(user1)           // auto-generated toString
```

**sealed class - для иерархий:**
```kotlin
sealed class Result {
    data class Success(val value: Int) : Result()
    data class Error(val message: String) : Result()
    object Loading : Result()
}

fun handle(result: Result) = when (result) {
    is Result.Success -> "Value: ${result.value}"
    is Result.Error -> "Error: ${result.message}"
    Result.Loading -> "Loading..."
    // Не нужен else - компилятор знает все типы!
}
```

**Когда что использовать:**

**data class:**
- API ответы и запросы
- Модели базы данных
- Конфигурация
- Value objects

**sealed class:**
- UI состояния (Loading, Success, Error)
- Навигация между экранами
- Результаты операций
- Конечные наборы типов

**Комбинация:**
```kotlin
sealed class PaymentMethod {
    data class CreditCard(val number: String) : PaymentMethod()
    data class PayPal(val email: String) : PaymentMethod()
    object Cash : PaymentMethod()
}

fun process(method: PaymentMethod) = when (method) {
    is PaymentMethod.CreditCard -> "Card: ${method.number}"  // data class benefits
    is PaymentMethod.PayPal -> "PayPal: ${method.email}"
    PaymentMethod.Cash -> "Cash"
}
```

**Ключевое отличие:**
- data class = "Какие данные здесь хранятся?"
- sealed class = "Какие возможны варианты/типы?"

## Related Questions

- [[q-value-classes-inline-classes--kotlin--medium]]
- [[q-coroutine-parent-child-relationship--kotlin--medium]]
- [[q-testing-viewmodel-coroutines--kotlin--medium]]

---
---
---id: kotlin-204
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
related: [c-aggregation, c-app-signing, c-backend, c-binary-search, c-binary-search-tree, c-binder, c-biometric-authentication, c-bm25-ranking, c-by-type, c-cap-theorem, c-ci-cd, c-ci-cd-pipelines, c-clean-code, c-compiler-optimization, c-compose-modifiers, c-compose-phases, c-compose-semantics, c-computer-science, c-concurrency, c-cross-platform-development, c-cross-platform-mobile, c-cs, c-data-classes, c-data-loading, c-debugging, c-declarative-programming, c-deep-linking, c-density-independent-pixels, c-dimension-units, c-dp-sp-units, c-dsl-builders, c-dynamic-programming, c-espresso-testing, c-event-handling, c-folder, c-functional-programming, c-gdpr-compliance, c-gesture-detection, c-gradle-build-cache, c-gradle-build-system, c-https-tls, c-image-formats, c-inheritance, c-jit-aot-compilation, c-kmm, c-kotlin, c-lambda-expressions, c-lazy-grid, c-lazy-initialization, c-level, c-load-balancing, c-manifest, c-memory-optimization, c-memory-profiler, c-microservices, c-multipart-form-data, c-multithreading, c-mutablestate, c-networking, c-offline-first-architecture, c-oop, c-oop-concepts, c-oop-fundamentals, c-oop-principles, c-play-console, c-play-feature-delivery, c-programming-languages, c-properties, c-real-time-communication, c-references, c-scaling-strategies, c-scoped-storage, c-sealed-classes, c-security, c-serialization, c-server-sent-events, c-shader-programming, c-snapshot-system, c-specific, c-strictmode, c-system-ui, c-test-doubles, c-test-sharding, c-testing-pyramid, c-testing-strategies, c-theming, c-to-folder, c-token-management, c-touch-input, c-turbine-testing, c-two-pointers, c-ui-testing, c-ui-ux-accessibility, c-value-classes, c-variable, c-weak-references, c-windowinsets, c-xml, q-value-classes-inline-classes--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [data-classes, difficulty/medium, programming-languages, sealed-classes]
---
# Вопрос (RU)
> В чём разница между data class и sealed class в Kotlin?

---

# Question (EN)
> What is the difference between data classes and sealed classes in Kotlin?

## Ответ (RU)

**data class** — класс для хранения данных с автогенерацией `equals()`, `hashCode()`, `copy()`, `toString()` и `componentN`.

**sealed class** — ограниченная иерархия типов, используемая с выражениями `when` для исчерпывающих проверок.

**Ключевые отличия:**

- `data class`:
  - Автогенерирует `equals()`, `hashCode()`, `toString()`, `copy()`, `componentN`.
  - Не может быть `abstract`, `open`, `sealed` или `inner`.
  - Подходит для хранения данных, DTO, моделей, value-объектов.
- `sealed class`:
  - Описывает закрытую иерархию типов с фиксированным набором подклассов.
  - Не генерирует вспомогательные методы автоматически (но подклассы могут быть `data class`).
  - Нельзя напрямую создавать экземпляры базового sealed-класса: обычно используем только его подклассы.
  - Используется для описания состояний, результатов операций, конечных наборов вариантов (finite type sets).

### Примеры

**data class — для данных:**
```kotlin
// Data class — хранит данные, автогенерирует полезные методы
data class User(val id: Int, val name: String, val email: String)

val user1 = User(1, "Alice", "alice@example.com")
val user2 = user1.copy(email = "new@example.com")
println(user1 == user2)  // false (автогенерированный equals)
println(user1)           // автогенерированный toString
```

**sealed class — для иерархий:**
```kotlin
// Sealed class — ограниченная иерархия для результатов
sealed class Result {
    data class Success(val value: Int) : Result()
    data class Error(val message: String) : Result()
    object Loading : Result()
}

fun handleResult(result: Result): String = when (result) {
    is Result.Success -> "Value: ${result.value}"
    is Result.Error -> "Error: ${result.message}"
    Result.Loading -> "Loading..."
    // else не нужен — компилятор знает все варианты
}
```

**Сравнение на примере:**

```kotlin
// DATA CLASS
data class Product(val id: Int, val name: String, val price: Double)

// Назначение: хранение данных
// Автоматически: equals, hashCode, toString, copy, componentN
// Нельзя объявить как: abstract, open, sealed, inner
// Use case: DTO, модели, value-объекты

fun demonstrateDataClass() {
    val p1 = Product(1, "Laptop", 999.99)
    val p2 = p1.copy(price = 899.99)

    println(p1)          // toString
    println(p1 == p2)    // equals
    println(p1.hashCode())

    val (id, name, price) = p1  // componentN (деструктуризация)
}

// SEALED CLASS
sealed class State {
    object Loading : State()
    data class Success(val data: String) : State()
    data class Error(val code: Int) : State()
}

// Назначение: ограниченная иерархия состояний
// Автогенерации нет у самого sealed-класса (но подклассы могут быть data class)
// Нельзя создавать напрямую экземпляр State, используем только подклассы.
// Use case: состояния, результаты, конечные наборы типов (finite type sets)

fun demonstrateSealedClass(state: State) {
    when (state) {  // исчерпывающий when
        State.Loading -> println("Loading...")
        is State.Success -> println("Data: ${state.data}")
        is State.Error -> println("Error: ${state.code}")
    }
}
```

**Когда что использовать:**

```kotlin
// DATA CLASS — когда нужно хранить данные

data class ApiResponse(
    val success: Boolean,
    val data: String?,
    val error: String?
)

data class UserEntity(
    val id: Long,
    val username: String,
    val email: String
)

data class AppConfig(
    val apiUrl: String,
    val timeout: Int,
    val debugMode: Boolean
)

// SEALED CLASS — когда нужно описать варианты/состояния

sealed class UiState {
    object Loading : UiState()
    data class Content(val items: List<String>) : UiState()
    data class Error(val message: String) : UiState()
}

sealed class Screen {
    object Home : Screen()
    data class Details(val id: Int) : Screen()
    object Settings : Screen()
}

sealed class NetworkResult<out T> {
    data class Success<out T>(val data: T) : NetworkResult<T>()
    data class Failure(val error: Throwable) : NetworkResult<Nothing>()
}
```

**Комбинация data и sealed:**

```kotlin
// Sealed class с data class-подклассами
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
            val (number, cvv, expiry) = method
            println("Charging $amount to card ending in ${number.takeLast(4)}")
        }
        is PaymentMethod.PayPal -> {
            println("Charging $amount to PayPal account ${method.email}")
        }
        PaymentMethod.Cash -> {
            println("Processing cash payment of $amount")
        }
    }
}
```

**Реальный пример (data + sealed + дженерики):**

```kotlin
// Data классы для моделей
data class User(val id: Int, val name: String)
data class Post(val id: Int, val title: String, val content: String)

// Sealed class для состояний загрузки с дженериками
sealed class LoadingState<out T> {
    object Idle : LoadingState<Nothing>()
    object Loading : LoadingState<Nothing>()
    data class Success<out T>(val data: T) : LoadingState<T>()
    data class Error(val exception: Throwable) : LoadingState<Nothing>()
}

fun fetchUser(id: Int): LoadingState<User> = try {
    val user = User(id, "Alice")
    LoadingState.Success(user)
} catch (e: Exception) {
    LoadingState.Error(e)
}

fun displayUserState(state: LoadingState<User>) {
    when (state) {
        LoadingState.Idle -> println("Not loaded")
        LoadingState.Loading -> println("Loading user...")
        is LoadingState.Success -> println("User: ${state.data.name} (ID: ${state.data.id})")
        is LoadingState.Error -> println("Error: ${state.exception.message}")
    }
}
```

**Итоговые отличия (кратко):**

```kotlin
/*
DATA CLASS:
- Для хранения данных.
- Генерирует: equals, hashCode, toString, copy, componentN.
- Нельзя объявить как abstract, open, sealed, inner.
- Используем для DTO, моделей, API-ответов, сущностей.

SEALED CLASS:
- Для описания иерархий и закрытых наборов вариантов.
- Сам sealed-класс ничего не генерирует автоматически (подклассы могут быть data class).
- Нельзя напрямую создавать экземпляр базового sealed-класса, используем только его подклассы.
- Используем для состояний, результатов, finite type sets, when-выражений.

КЛЮЧЕВОЕ:
- data class = "Какие данные здесь хранятся?"
- sealed class = "Какие возможны варианты/состояния?"
*/
```

## Answer (EN)

**data class** — A class for storing data with auto-generation of `equals()`, `hashCode()`, `copy()`, `toString()`, and `componentN`.

**sealed class** — A restricted class hierarchy, used with `when` expressions for exhaustive checks.

**Key differences:**

- `data class`:
  - Automatically creates `equals()`, `hashCode()`, `toString()`, `copy()`, `componentN`.
  - Cannot be `abstract`, `open`, `sealed`, or `inner`.
  - Used for data containers: DTOs, models, value objects.
- `sealed class`:
  - Describes a closed hierarchy with a fixed set of subclasses (finite type sets).
  - The sealed base class itself does not auto-generate helper methods (subclasses can be `data class`).
  - Cannot be instantiated directly in practice; you work only with its subclasses.
  - Used for representing states, operation results, and closed sets of variants.

### Code Examples

**data class - for data:**

```kotlin
// Data class - stores data and auto-generates useful methods
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
// Sealed class - represents a restricted result hierarchy
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

**Comparison (in code comments):**

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

    println(p1)              // toString
    println(p1 == p2)        // equals
    println(p1.hashCode())   // hashCode

    val (id, name, price) = p1  // componentN
}

// SEALED CLASS
sealed class State {
    object Loading : State()
    data class Success(val data: String) : State()
    data class Error(val code: Int) : State()
}

// Purpose: Restricted type hierarchy (finite type set)
// Auto-generated: none on the sealed base (subclasses may be data classes)
// Cannot be instantiated directly; use its subclasses only.
// Use case: state management, result types, finite sets of types

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
    data class Success<out T>(val data: T) : NetworkResult<T>()
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
            println("Charging $amount to card ending in ${number.takeLast(4)}")
        }
        is PaymentMethod.PayPal -> {
            println("Charging $amount to PayPal account ${method.email}")
        }
        PaymentMethod.Cash -> {
            println("Processing cash payment of $amount")
        }
    }
}
```

**Real-world example:**

```kotlin
// Data classes for models
data class User(val id: Int, val name: String)
data class Post(val id: Int, val title: String, val content: String)

// Sealed class for loading states
sealed class LoadingState<out T> {
    object Idle : LoadingState<Nothing>()
    object Loading : LoadingState<Nothing>()
    data class Success<out T>(val data: T) : LoadingState<T>()
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
```

**Summary of differences:**

```kotlin
/*
DATA CLASS:
- Purpose: Data containers.
- Auto-generates: equals, hashCode, toString, copy, componentN.
- Cannot be: abstract, open, sealed, inner.
- Use for: DTOs, models, API responses, entities.

SEALED CLASS:
- Purpose: Type hierarchies and closed sets of variants (finite type sets).
- Auto-generates: nothing on the sealed base (subclasses can be data classes).
- Cannot be instantiated directly; use only its subclasses.
- Use for: states, results, finite type sets, when expressions.

KEY DIFFERENCE:
- data class = "What data does this contain?"
- sealed class = "What are all possible variants/states?"
*/
```

---

## Дополнительные Вопросы (RU)

- В чём ключевые отличия этого подхода от Java?
- Когда вы бы использовали data и sealed классы на практике?
- Какие распространённые ошибки при использовании data и sealed классов?

## Ссылки (RU)

- [[c-kotlin]]
- [[c-sealed-classes]]

## Связанные Вопросы (RU)

- [[q-value-classes-inline-classes--kotlin--medium]]
- [[q-coroutine-parent-child-relationship--kotlin--medium]]
- [[q-testing-viewmodel-coroutines--kotlin--medium]]

## Follow-ups

- What are the key differences between this and Java?
- When would you use data and sealed classes in practice?
- What are common mistakes when using data and sealed classes?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-value-classes-inline-classes--kotlin--medium]]
- [[q-coroutine-parent-child-relationship--kotlin--medium]]
- [[q-testing-viewmodel-coroutines--kotlin--medium]]

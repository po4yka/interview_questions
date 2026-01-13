---
---
---id: kotlin-152
title: "Describe Data and Sealed Classes / Описание Data и Sealed классов"
aliases: [Data и Sealed классы описание, Describe Data Sealed Classes]
topic: kotlin
subtopics: [data-classes, sealed-classes]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-aggregation, c-app-signing, c-backend, c-binary-search, c-binary-search-tree, c-binder, c-biometric-authentication, c-bm25-ranking, c-by-type, c-cap-theorem, c-ci-cd, c-ci-cd-pipelines, c-clean-code, c-compiler-optimization, c-compose-modifiers, c-compose-phases, c-compose-semantics, c-computer-science, c-concurrency, c-cross-platform-development, c-cross-platform-mobile, c-cs, c-data-classes, c-data-loading, c-debugging, c-declarative-programming, c-deep-linking, c-density-independent-pixels, c-dimension-units, c-dp-sp-units, c-dsl-builders, c-dynamic-programming, c-espresso-testing, c-event-handling, c-folder, c-functional-programming, c-gdpr-compliance, c-gesture-detection, c-gradle-build-cache, c-gradle-build-system, c-https-tls, c-image-formats, c-inheritance, c-jit-aot-compilation, c-kmm, c-kotlin, c-lambda-expressions, c-lazy-grid, c-lazy-initialization, c-level, c-load-balancing, c-manifest, c-memory-optimization, c-memory-profiler, c-microservices, c-multipart-form-data, c-multithreading, c-mutablestate, c-networking, c-offline-first-architecture, c-oop, c-oop-concepts, c-oop-fundamentals, c-oop-principles, c-play-console, c-play-feature-delivery, c-programming-languages, c-properties, c-real-time-communication, c-references, c-scaling-strategies, c-scoped-storage, c-sealed-classes, c-security, c-serialization, c-server-sent-events, c-shader-programming, c-snapshot-system, c-specific, c-strictmode, c-system-ui, c-test-doubles, c-test-sharding, c-testing-pyramid, c-testing-strategies, c-theming, c-to-folder, c-token-management, c-touch-input, c-turbine-testing, c-two-pointers, c-ui-testing, c-ui-ux-accessibility, c-value-classes, c-variable, c-weak-references, c-windowinsets, c-xml, q-kotlin-sam-interfaces--kotlin--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [data-classes, difficulty/medium, programming-languages, sealed-classes]

---
# Вопрос (RU)
> Опишите data классы и sealed классы в Kotlin. Каковы их ключевые особенности и применения?

---

# Question (EN)
> Describe data classes and sealed classes in Kotlin. What are their key features and use cases?

## Ответ (RU)

### Data Классы

**Data классы** в Kotlin предназначены для хранения данных и автоматически генерируют методы: `equals()`, `hashCode()`, `toString()` и `copy()`, а также компонентные функции для деструктуризации. Они идеально подходят для создания POJO/POCO объектов (Plain Old Java/C# Objects). Важно помнить, что data классы сами по себе не гарантируют неизменяемость — она достигается за счёт использования `val` свойств и отсутствия изменяемых полей.

Также важно учитывать несколько ограничений data классов:
- Должен быть как минимум один параметр в primary-конструкторе.
- Класс не может быть `open`, `abstract`, `sealed` или `inner`.
- Наследование от data класса возможно, но сам data класс не может быть `open`.

**Ключевые особенности data классов:**
- Автоматическая генерация utility-методов (`equals()`, `hashCode()`, `toString()`, `copy()`, componentN)
- Встроенная поддержка деструктуризации (destructuring declarations)
- Возможность легко реализовать immutability, если использовать только `val` и не держать изменяемые ссылки
- Простое копирование объектов с изменениями через `copy()`
- Идеальны для DTOs, моделей и value objects

**Пример:**
```kotlin
data class User(
    val id: Int,
    val username: String,
    val email: String,
    val age: Int
)

val user = User(1, "alice", "alice@example.com", 30)

// Автоматический toString()
println(user)
// User(id=1, username=alice, email=alice@example.com, age=30)

// Автоматический equals()
val sameUser = User(1, "alice", "alice@example.com", 30)
println(user == sameUser)  // true

// copy() для создания изменённых экземпляров
val olderUser = user.copy(age = 31)
println(olderUser)
// User(id=1, username=alice, email=alice@example.com, age=31)

// Деструктуризация
val (id, username, email, age) = user
println("Пользователь $username, возраст $age лет")
```

**Data класс как POJO/DTO:**
```kotlin
// API response модель
data class LoginResponse(
    val success: Boolean,
    val token: String?,
    val userId: Int?,
    val message: String,
    val expiresAt: Long?
)

// Request модель
data class LoginRequest(
    val username: String,
    val password: String,
    val rememberMe: Boolean = false
)

// Domain модель
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
```

### Sealed Классы

**Sealed классы** используются для представления ограниченного набора подтипов, похожих на перечисления, но с возможностью иметь классы с разными свойствами и методами. Это обеспечивает безопасное использование при работе с типами во время компиляции, улучшая обработку ошибок и логику ветвления. Sealed класс сам по себе является абстрактным и не может быть создан напрямую.

**Ключевые особенности sealed классов:**
- Ограниченные иерархии классов
- Compile-time exhaustiveness checking в `when` выражениях
- Типобезопасное представление конечного множества состояний
- Идеальны для управления состоянием и Result типов
- Подклассы должны находиться в контролируемой области: в классическом варианте — в том же файле, в более новых версиях Kotlin — могут быть распределены по нескольким файлам в пределах одного compilation unit (например, одного модуля), что по-прежнему сохраняет ограниченность иерархии

**Пример:**
```kotlin
// Sealed класс для представления различных состояний
sealed class NetworkState {
    object Idle : NetworkState()
    object Loading : NetworkState()
    data class Success(val data: String, val timestamp: Long) : NetworkState()
    data class Error(val exception: Throwable, val retryable: Boolean) : NetworkState()
}

// Функция, обрабатывающая все возможные состояния
fun handleNetworkState(state: NetworkState) {
    when (state) {  // else не нужен - компилятор знает все случаи
        NetworkState.Idle -> {
            println("Сеть в состоянии ожидания")
        }
        NetworkState.Loading -> {
            println("Загрузка данных...")
        }
        is NetworkState.Success -> {
            println("Успех! Данные: ${state.data}")
            println("Получено в: ${state.timestamp}")
        }
        is NetworkState.Error -> {
            println("Ошибка: ${state.exception.message}")
            if (state.retryable) {
                println("Можно повторить операцию")
            }
        }
    }
}
```

**Sealed класс с разными свойствами:**
```kotlin
// Типы платежных методов - каждый с разными свойствами
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
            println("Обработка платежа кредитной картой на $$amount")
            println("Карта оканчивается на: ${method.cardNumber.takeLast(4)}")
            println("Владелец: ${method.cardholderName}")
        }
        is PaymentMethod.PayPal -> {
            println("Обработка PayPal платежа на $$amount")
            println("PayPal аккаунт: ${method.email}")
            if (!method.verified) {
                println("Предупреждение: Аккаунт не верифицирован")
            }
        }
        is PaymentMethod.BankTransfer -> {
            println("Обработка банковского перевода на $$amount")
            println("Банк: ${method.bankName}")
            println("Счёт: ${method.accountNumber}")
        }
        PaymentMethod.Cash -> {
            println("Обработка наличного платежа на $$amount")
            println("Подготовьте точную сумму")
        }
        is PaymentMethod.Cryptocurrency -> {
            println("Обработка криптовалютного платежа на $$amount")
            println("Валюта: ${method.currency}")
            println("Кошелёк: ${method.walletAddress}")
        }
    }
}
```

### Комбинирование Data Классов С Sealed Классами

**Универсальный Result тип:**
```kotlin
// Универсальный result тип используя sealed класс и data классы
sealed class Result<out T> {
    data class Success<out T>(val value: T) : Result<T>()
    data class Failure(val error: Error) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Типы ошибок
data class Error(
    val code: Int,
    val message: String,
    val details: Map<String, String> = emptyMap()
)

// Domain модели
data class Article(
    val id: Int,
    val title: String,
    val content: String,
    val author: String,
    val publishedAt: Long
)

// Service слой
class ArticleService {
    fun fetchArticle(id: Int): Result<Article> {
        return try {
            if (id > 0) {
                Result.Success(
                    Article(
                        id = id,
                        title = "Лучшие практики Kotlin",
                        content = "Вот несколько лучших практик...",
                        author = "Иван Иванов",
                        publishedAt = System.currentTimeMillis()
                    )
                )
            } else {
                Result.Failure(
                    Error(404, "Статья не найдена", mapOf("article_id" to id.toString()))
                )
            }
        } catch (e: Exception) {
            Result.Failure(
                Error(500, "Ошибка сервера", mapOf("exception" to e.message.orEmpty()))
            )
        }
    }
}

// UI слой
fun displayArticle(result: Result<Article>) {
    when (result) {
        is Result.Success -> {
            val article = result.value
            println("Заголовок: ${article.title}")
            println("Автор: ${article.author}")
            println("Содержание: ${article.content}")
        }
        is Result.Failure -> {
            println("Ошибка ${result.error.code}: ${result.error.message}")
            if (result.error.details.isNotEmpty()) {
                println("Детали: ${result.error.details}")
            }
        }
        Result.Loading -> {
            println("Загрузка статьи...")
        }
    }
}
```

**Реальный пример: Валидация формы:**
```kotlin
// Данные формы (data класс)
data class RegistrationForm(
    val username: String,
    val email: String,
    val password: String,
    val confirmPassword: String,
    val agreeToTerms: Boolean
)

// Результат валидации (sealed класс)
sealed class ValidationResult {
    data class Valid(val form: RegistrationForm) : ValidationResult()
    data class Invalid(val errors: List<ValidationError>) : ValidationResult()
}

// Типы ошибок (data класс)
data class ValidationError(
    val field: String,
    val message: String
)

fun validateRegistration(form: RegistrationForm): ValidationResult {
    val errors = mutableListOf<ValidationError>()

    if (form.username.length < 3) {
        errors.add(ValidationError("username", "Имя пользователя должно быть не менее 3 символов"))
    }

    if (!form.email.contains("@") || !form.email.contains(".")) {
        errors.add(ValidationError("email", "Неверный формат email"))
    }

    if (form.password.length < 8) {
        errors.add(ValidationError("password", "Пароль должен быть не менее 8 символов"))
    }

    if (form.password != form.confirmPassword) {
        errors.add(ValidationError("confirmPassword", "Пароли не совпадают"))
    }

    if (!form.agreeToTerms) {
        errors.add(ValidationError("agreeToTerms", "Необходимо согласие с условиями"))
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
            println("Форма валидна!")
            println("Регистрация пользователя: ${result.form.username}")
            println("Email: ${result.form.email}")
        }
        is ValidationResult.Invalid -> {
            println("Форма содержит ${result.errors.size} ошибок:")
            result.errors.forEach { error ->
                println("  - ${error.field}: ${error.message}")
            }
        }
    }
}
```

## Краткая Версия
**Data классы**: Предназначены для хранения данных. Автоматически генерируют `equals()`, `hashCode()`, `toString()`, `copy()` и компонентные функции. Идеальны для POJO/POCO объектов, DTOs, моделей данных и value objects. Поддерживают деструктуризацию и простое копирование с изменениями. Не делают объекты неизменяемыми автоматически — это достигается выбором типов свойств и API.

**Sealed классы**: Представляют ограниченный набор типов. Ограничивают наследование контролируемой областью и позволяют компилятору проверять исчерпывающий разбор в `when` выражениях. Идеальны для управления состоянием, Result типов, навигационных событий и представления конечных множеств состояний. Хорошо комбинируются с data классами для создания надёжных type-safe API.

## Short Version
**Data classes**: Designed for holding data. Automatically generate `equals()`, `hashCode()`, `toString()`, `copy()`, and component functions. Ideal for POJO/POCO objects, DTOs, data models, and value objects. Support destructuring and easy copying with modifications. Do not make objects immutable by default — immutability is achieved via property choices and API design.

**Sealed classes**: Represent a restricted set of types. Constrain inheritance to a controlled scope and enable the compiler to enforce exhaustive `when` expressions. Ideal for modeling state, result types, navigation events, and finite state sets. Combine well with data classes to build robust type-safe APIs.

## Answer (EN)

**Data Classes:**
Data classes in Kotlin are designed for storing data and automatically generate methods such as `equals()`, `hashCode()`, `toString()`, `copy()`, and component functions for destructuring. They are ideal for creating POJO/POCO objects (Plain Old Java/C# Objects). Note that data classes do not inherently guarantee immutability; immutability is achieved by using `val` properties and avoiding mutable state.

Additionally, data classes have a few important constraints:
- The primary constructor must have at least one parameter.
- A data class cannot be `open`, `abstract`, `sealed`, or `inner`.
- Inheritance from a data class is possible (e.g., if it extends another type), but the data class itself cannot be declared `open`.

**Key features of data classes:**
- Automatic generation of utility methods (`equals()`, `hashCode()`, `toString()`, `copy()`, componentN)
- Built-in support for destructuring declarations
- Easy to make immutable by using `val` properties and not exposing mutable fields
- Easy object copying with modifications via `copy()`
- Perfect for DTOs, models, and value objects

**Sealed Classes:**
Sealed classes are used to represent a restricted set of types, similar to enums, but with the ability to have subclasses with different properties and methods. This helps ensure safe usage when working with types at compile time, improving error handling and branching logic. A sealed class itself is abstract and cannot be instantiated directly.

**Key features of sealed classes:**
- Restricted class hierarchies
- Compile-time exhaustiveness checking in `when` expressions
- Type-safe representation of a finite set of states
- Great for state management and result types
- Subclasses must be declared within a controlled scope: in classic sealed semantics within the same file; in newer Kotlin versions they may be distributed across multiple files within the same compilation unit (e.g., module), preserving a closed hierarchy

### Code Examples

(Each of the following code snippets is a standalone example; in a real project they would typically live in separate files / scopes rather than sharing multiple `main` functions.)

**Data class comprehensive example:**

```kotlin
// Simple data class for user data
data class User(
    val id: Int,
    val username: String,
    val email: String,
    val age: Int
)

fun useUser() {
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

fun useLogin() {
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
```

**Combining data classes with sealed classes:**

```kotlin
// Generic result type using sealed class and data classes
sealed class Result<out T> {
    data class Success<out T>(val value: T) : Result<T>()
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
```

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия data и sealed классов от аналогичных конструкций в Java?
- Когда вы бы использовали эти конструкции на практике?
- Какие распространенные ошибки и подводные камни следует избегать при использовании data и sealed классов?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-sealed-classes]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-sealed-classes]]

## Связанные Вопросы (RU)

- [[q-kotlin-immutable-collections--kotlin--easy]]
- [[q-kotlin-sam-interfaces--kotlin--medium]]

## Related Questions

- [[q-kotlin-immutable-collections--kotlin--easy]]
- [[q-kotlin-sam-interfaces--kotlin--medium]]

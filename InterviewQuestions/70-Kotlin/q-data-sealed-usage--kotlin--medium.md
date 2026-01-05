---
id: kotlin-213
title: "Data Sealed Usage / Data Sealed Использование"
aliases: [Data Sealed Classes Usage, Data и Sealed использование]
topic: kotlin
subtopics: [data-classes, sealed-classes]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-sealed-classes]
created: 2025-10-15
updated: 2025-11-09
tags: [data-classes, difficulty/medium, sealed-classes]
---
# Вопрос (RU)
> Для чего используются `data` классы и `sealed` классы в Kotlin? Каковы их практические применения?

---

# Question (EN)
> What are data classes and sealed classes used for in Kotlin? What are their practical applications?

## Ответ (RU)

### `data` Классы — Для Хранения И Работы С Данными

`data class` используется для хранения и работы с данными. Удобны при:
- копировании — метод `copy()` для создания изменённых копий;
- логическом сравнении — автоматический `equals()` сравнивает по содержимому;
- сериализации — легко преобразуются в JSON/XML и обратно;
- деструктуризации — компонентные функции `componentN()`.

Основные применения `data` классов:
- DTO (Data Transfer Objects) для API;
- модели данных в приложениях;
- API responses и requests;
- сущности базы данных;
- configuration-объекты;
- неизменяемые состояния.

#### Пример: Копирование
```kotlin
data class UserResponse(
    val id: Int,
    val username: String,
    val email: String,
    val isActive: Boolean
)

val user = UserResponse(1, "alice", "alice@example.com", true)

// Создание изменённых копий
val deactivatedUser = user.copy(isActive = false)
val renamedUser = user.copy(username = "alice_smith")

println(user)               // Оригинал не изменён
println(deactivatedUser)    // Изменён только isActive
println(renamedUser)        // Изменён только username
```

#### Пример: Логическое Сравнение И Коллекции
```kotlin
data class Point(val x: Int, val y: Int)

val p1 = Point(10, 20)
val p2 = Point(10, 20)
val p3 = Point(15, 25)

println("p1 == p2: ${p1 == p2}")    // true - сравнение по содержимому
println("p1 === p2: ${p1 === p2}")  // false - разные ссылки
println("p1 == p3: ${p1 == p3}")    // false - разные значения

// Работает в коллекциях
data class Order(val id: String, val items: List<String>, val total: Double)

val order1 = Order("ORD-001", listOf("Laptop", "Mouse"), 1029.99)
val order2 = Order("ORD-001", listOf("Laptop", "Mouse"), 1029.99)

println("order1 == order2: ${order1 == order2}")  // true

val uniqueOrders = setOf(order1, order2)
println("Уникальных заказов: ${uniqueOrders.size}")  // 1
```

#### Пример: Сериализация
```kotlin
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

val product = Product(1, "Laptop", 999.99, true)
val item = CartItem(product, 2)

// Сериализация в JSON
val json = Json.encodeToString(item)
println("JSON: $json")

// Десериализация из JSON
val restored = Json.decodeFromString<CartItem>(json)
println("Восстановлено: $restored")

// Благодаря equals() можно удобно сравнивать
println("Равны: ${item == restored}")  // true
```

### `sealed` Классы — Для Ограниченного Набора Подтипов

`sealed class` используется для ограниченного набора подтипов. Удобны при использовании `when`, так как все случаи должны быть обработаны — это повышает безопасность и читаемость.

Основные применения `sealed` классов:
- управление UI-состояниями (`Loading`, `Success`, `Error`);
- типы результатов операций;
- навигационные события;
- обработка ошибок с разными типами ошибок;
- state machine;
- command-паттерны.

#### Пример: `when` С Исчерпывающей Обработкой
```kotlin
sealed class Operation {
    data class Add(val a: Int, val b: Int) : Operation()
    data class Subtract(val a: Int, val b: Int) : Operation()
    data class Multiply(val a: Int, val b: Int) : Operation()
    data class Divide(val a: Int, val b: Int) : Operation()
}

fun calculate(operation: Operation): Double {
    // Все случаи должны быть обработаны - компилятор проверяет
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
        // else не нужен - компилятор знает все варианты
    }
}

println(calculate(Operation.Add(10, 5)))       // 15.0
println(calculate(Operation.Subtract(10, 5)))  // 5.0
println(calculate(Operation.Multiply(10, 5)))  // 50.0
println(calculate(Operation.Divide(10, 5)))    // 2.0
println(calculate(Operation.Divide(10, 0)))    // NaN
```

#### Пример: Типобезопасное Управление Состоянием UI
```kotlin
// Типобезопасное управление состоянием
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
        try {
            val data = listOf("Элемент 1", "Элемент 2", "Элемент 3")
            state = UiState.Success(data)
        } catch (e: Exception) {
            state = UiState.Error(e.message ?: "Неизвестная ошибка")
        }
    }

    fun getState() = state
}

// UI-слой - типобезопасная обработка
fun render(state: UiState<List<String>>) {
    when (state) {
        UiState.Initial -> {
            println("Нажмите кнопку для загрузки данных")
        }
        UiState.Loading -> {
            println("Загрузка...")
        }
        is UiState.Success -> {
            println("Данные загружены:")
            state.data.forEach { println("  - $it") }
        }
        is UiState.Error -> {
            println("Ошибка: ${state.message}")
            state.code?.let { println("Код ошибки: $it") }
        }
    }
}
```

### Комбинация: API-клиент

Очень распространённый паттерн — `data` классы для данных + `sealed` классы для результатов:

```kotlin
// Data-классы для requests/responses
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

// Sealed-класс для результатов
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val code: Int, val message: String) : ApiResult<Nothing>()
    object NetworkError : ApiResult<Nothing>()
}

class ApiClient {
    fun login(request: LoginRequest): ApiResult<UserData> {
        return try {
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
                ApiResult.Error(401, "Неверные учётные данные")
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
            println("Вход успешен!")
            println("Добро пожаловать, ${user.username}")
            println("Токен: ${user.token}")
        }
        is ApiResult.Error -> {
            println("Ошибка входа: ${result.message} (код: ${result.code})")
        }
        ApiResult.NetworkError -> {
            println("Ошибка сети. Проверьте подключение.")
        }
    }
}
```

### Валидация Формы

```kotlin
// Data-класс для данных формы
data class RegistrationForm(
    val username: String,
    val email: String,
    val password: String,
    val confirmPassword: String
)

// Sealed-класс для результата валидации
sealed class ValidationResult {
    data class Valid(val form: RegistrationForm) : ValidationResult()
    data class Invalid(val errors: Map<String, String>) : ValidationResult()
}

fun validateForm(form: RegistrationForm): ValidationResult {
    val errors = mutableMapOf<String, String>()

    if (form.username.length < 3) {
        errors["username"] = "Имя должно быть не менее 3 символов"
    }

    if (!form.email.contains("@")) {
        errors["email"] = "Неверный формат email"
    }

    if (form.password.length < 8) {
        errors["password"] = "Пароль должен быть не менее 8 символов"
    }

    if (form.password != form.confirmPassword) {
        errors["confirmPassword"] = "Пароли не совпадают"
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
            println("Регистрация успешна!")
            println("Пользователь: $username")
            println("Email: $email")
        }
        is ValidationResult.Invalid -> {
            println("Ошибки валидации:")
            result.errors.forEach { (field, error) ->
                println("  $field: $error")
            }
        }
    }
}
```

### Краткий Ответ

`data class` — для хранения и работы с данными:
- автоматическое копирование (`copy()`);
- логическое сравнение (`equals()`);
- сериализация в JSON/XML;
- используется для DTO, моделей, API-ответов, сущностей БД.

`sealed class` — для ограниченного набора подтипов:
- типобезопасная обработка в `when` (исчерпывающая проверка);
- повышает безопасность и читаемость;
- используется для UI-состояний, типов результатов, навигации и обработки ошибок.

Лучшая практика: комбинировать `data` классы для данных и `sealed` классы для результатов/состояний.

## Answer (EN)

`data class` — used for storing and working with data. Convenient for copying, logical comparison, destructuring, and serialization.

`sealed class` — used for a restricted set of subtypes. Convenient with `when` expressions because the compiler can enforce exhaustive handling, improving safety and readability.

Key use cases:
- `data class`: DTOs, models, API responses, database entities, configuration objects, immutable state;
- `sealed class`: state management, result types, navigation events, error handling, state machines, command patterns.

### Code Examples

#### `data class` For Data Storage
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
```

#### `data class` For Logical Comparison
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

    println("p1 == p2: ${p1 == p2}")   // true - content equality
    println("p1 === p2: ${p1 === p2}") // false - different references
    println("p1 == p3: ${p1 == p3}")   // false - different values

    // Complex objects
    val order1 = Order("ORD-001", listOf("Laptop", "Mouse"), 1029.99)
    val order2 = Order("ORD-001", listOf("Laptop", "Mouse"), 1029.99)

    println("order1 == order2: ${order1 == order2}")  // true

    // Works in collections
    val uniqueOrders = setOf(order1, order2)
    println("Unique orders: ${uniqueOrders.size}")  // 1
}
```

#### `data class` For Serialization
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

    // Uses equals() for content comparison
    println("Equal: ${item == restored}")  // true
}
```

### `sealed class` For Exhaustive `when`

```kotlin
sealed class Operation {
    data class Add(val a: Int, val b: Int) : Operation()
    data class Subtract(val a: Int, val b: Int) : Operation()
    data class Multiply(val a: Int, val b: Int) : Operation()
    data class Divide(val a: Int, val b: Int) : Operation()
}

fun calculate(operation: Operation): Double {
    // All cases must be handled - compiler enforces this
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
        // No else needed - compiler knows all subclasses
    }
}
```

### `sealed class` For Safety and Readability

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
```

### Combined Example: API Client

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
            // Simulated API call
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
```

### Real-world Form Validation

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
```

---

## Дополнительные Вопросы (RU)

- В чём ключевые отличия `data` и `sealed` классов от аналогов в Java?
- В каких практических сценариях вы бы использовали `data` и `sealed` классы?
- Каковы типичные ошибки при использовании `data` и `sealed` классов?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- Официальная документация Kotlin: https://kotlinlang.org/docs/home.html
- [[c-kotlin]]

## References

- Kotlin Documentation: https://kotlinlang.org/docs/home.html
- [[c-kotlin]]

## Связанные Вопросы (RU)

- [[q-kotlin-extension-functions-advanced--kotlin--hard]]
- [[q-kotlin-higher-order-functions--kotlin--medium]]
- [[q-kotlin-equals-hashcode-purpose--kotlin--medium]]

## Related Questions

- [[q-kotlin-extension-functions-advanced--kotlin--hard]]
- [[q-kotlin-higher-order-functions--kotlin--medium]]
- [[q-kotlin-equals-hashcode-purpose--kotlin--medium]]

---
id: 20251012-400006
title: "Kotlin Value Classes (Inline Classes) / Value классы в Kotlin"
topic: android
difficulty: medium
status: draft
created: 2025-10-12
tags: [value-classes, inline-classes, performance, type-safety, android/value-classes, android/inline-classes, android/performance, android/type-safety, difficulty/medium]
moc: moc-android
related: [q-api-file-upload-server--android--medium, q-until-what-point-does-viewmodel-guarantee-state-preservation--android--medium, q-kmm-ktor-networking--multiplatform--medium]
  - q-kotlin-coroutines-advanced--kotlin--hard
  - q-sealed-classes-state-management--kotlin--medium
  - q-compose-performance-optimization--android--hard
subtopics:
  - kotlin
  - value-classes
  - inline-classes
  - performance
  - type-safety
---
# Kotlin Value Classes (Inline Classes)

## English Version

### Problem Statement

Value classes (formerly inline classes) provide zero-overhead type-safe wrappers around primitive types. They enable creating strongly-typed domain models without runtime performance penalties, essential for performance-critical Android applications.

**The Question:** What are value classes? How do they differ from data classes? When should you use them? What are the performance benefits and limitations?

### Detailed Answer

---

### VALUE CLASS BASICS

**Definition:**
```kotlin
@JvmInline
value class UserId(val value: String)

@JvmInline
value class Email(val value: String)

@JvmInline
value class Amount(val value: Double)

// Usage - type safety without runtime overhead
fun getUser(userId: UserId): User {
    // Can't accidentally pass Email here 
    return userRepository.findById(userId.value)
}

fun sendEmail(email: Email, subject: String) {
    // Type-safe email handling
}

val userId = UserId("user123")
val email = Email("user@example.com")

// Compile error 
// getUser(email)  // Type mismatch
```

**Key features:**
```
 Zero runtime overhead (inlined at compile time)
 Type safety at compile time
 Must have single property in primary constructor
 Property must be immutable (val, not var)
 Replaces inline classes (deprecated in Kotlin 1.5)
 @JvmInline annotation required
```

---

### VALUE CLASS VS DATA CLASS

```kotlin
// Data class - regular object allocation
data class UserIdData(val value: String)

// Value class - no object allocation
@JvmInline
value class UserIdValue(val value: String)

// Performance comparison
fun testPerformance() {
    // Data class: allocates object on heap
    val dataId = UserIdData("123")  // Heap allocation 

    // Value class: no allocation, inlined to String
    val valueId = UserIdValue("123")  // No allocation 

    // At runtime, valueId is just "123"
}

// Memory usage:
// Data class: Object header + String reference = ~16 bytes
// Value class: Just the String = 0 extra bytes
```

---

### TYPE-SAFE DOMAIN MODELS

```kotlin
// Problem: Primitive obsession
fun createOrder(
    customerId: String,
    productId: String,
    quantity: Int,
    price: Double
) {
    // Easy to mix up parameters 
    // createOrder("product123", "customer456", 10, 99.99)
}

// Solution: Value classes
@JvmInline
value class CustomerId(val value: String)

@JvmInline
value class ProductId(val value: String)

@JvmInline
value class Quantity(val value: Int) {
    init {
        require(value > 0) { "Quantity must be positive" }
    }
}

@JvmInline
value class Price(val value: Double) {
    init {
        require(value >= 0) { "Price must be non-negative" }
    }
}

fun createOrder(
    customerId: CustomerId,
    productId: ProductId,
    quantity: Quantity,
    price: Price
) {
    // Impossible to mix up parameters 
    // Type-safe and self-documenting
}

// Usage
val order = createOrder(
    customerId = CustomerId("customer456"),
    productId = ProductId("product123"),
    quantity = Quantity(10),
    price = Price(99.99)
)
```

---

### VALIDATION IN VALUE CLASSES

```kotlin
@JvmInline
value class Email(val value: String) {
    init {
        require(value.contains("@")) { "Invalid email format" }
        require(value.length <= 100) { "Email too long" }
    }

    fun domain(): String = value.substringAfter("@")
    fun localPart(): String = value.substringBefore("@")
}

@JvmInline
value class PhoneNumber(val value: String) {
    init {
        val digits = value.filter { it.isDigit() }
        require(digits.length in 10..15) { "Invalid phone number" }
    }

    fun formatted(): String {
        val digits = value.filter { it.isDigit() }
        return when (digits.length) {
            10 -> "${digits.substring(0, 3)}-${digits.substring(3, 6)}-${digits.substring(6)}"
            11 -> "+${digits[0]} ${digits.substring(1, 4)}-${digits.substring(4, 7)}-${digits.substring(7)}"
            else -> value
        }
    }
}

@JvmInline
value class Password(val value: String) {
    init {
        require(value.length >= 8) { "Password must be at least 8 characters" }
        require(value.any { it.isUpperCase() }) { "Password must contain uppercase" }
        require(value.any { it.isDigit() }) { "Password must contain digit" }
    }

    fun strength(): PasswordStrength {
        return when {
            value.length >= 12 && value.any { !it.isLetterOrDigit() } -> PasswordStrength.STRONG
            value.length >= 10 -> PasswordStrength.MEDIUM
            else -> PasswordStrength.WEAK
        }
    }
}

enum class PasswordStrength { WEAK, MEDIUM, STRONG }

// Usage
try {
    val email = Email("user@example.com")
    val phone = PhoneNumber("1234567890")
    val password = Password("SecurePass123")

    println("Email domain: ${email.domain()}")
    println("Phone formatted: ${phone.formatted()}")
    println("Password strength: ${password.strength()}")
} catch (e: IllegalArgumentException) {
    println("Validation error: ${e.message}")
}
```

---

### COMMON USE CASES

#### 1. IDs and Identifiers

```kotlin
@JvmInline
value class UserId(val value: String)

@JvmInline
value class OrderId(val value: Long)

@JvmInline
value class SessionToken(val value: String) {
    fun isExpired(): Boolean {
        // Check token expiration
        return false
    }
}

class UserRepository {
    private val users = mutableMapOf<UserId, User>()

    fun findById(id: UserId): User? = users[id]

    fun save(user: User) {
        users[user.id] = user
    }
}

data class User(
    val id: UserId,
    val email: Email,
    val name: String
)
```

---

#### 2. Measurements and Units

```kotlin
@JvmInline
value class Meters(val value: Double) {
    fun toKilometers(): Kilometers = Kilometers(value / 1000)
    fun toMiles(): Miles = Miles(value * 0.000621371)
}

@JvmInline
value class Kilometers(val value: Double) {
    fun toMeters(): Meters = Meters(value * 1000)
}

@JvmInline
value class Miles(val value: Double) {
    fun toMeters(): Meters = Meters(value * 1609.344)
}

@JvmInline
value class Kilograms(val value: Double) {
    fun toPounds(): Pounds = Pounds(value * 2.20462)
}

@JvmInline
value class Pounds(val value: Double) {
    fun toKilograms(): Kilograms = Kilograms(value / 2.20462)
}

// Usage - impossible to mix up units
fun calculateShippingCost(distance: Kilometers, weight: Kilograms): Price {
    val distanceInMiles = distance.toMeters().toMiles()
    val weightInPounds = weight.toPounds()

    val cost = distanceInMiles.value * 0.5 + weightInPounds.value * 0.1
    return Price(cost)
}

val distance = Kilometers(100.0)
val weight = Kilograms(5.0)
val cost = calculateShippingCost(distance, weight)
```

---

#### 3. Money and Currency

```kotlin
@JvmInline
value class USD(val cents: Long) {
    constructor(dollars: Double) : this((dollars * 100).toLong())

    fun toDollars(): Double = cents / 100.0

    operator fun plus(other: USD): USD = USD(cents + other.cents)
    operator fun minus(other: USD): USD = USD(cents - other.cents)
    operator fun times(multiplier: Int): USD = USD(cents * multiplier)
    operator fun div(divisor: Int): USD = USD(cents / divisor)

    override fun toString(): String = "$${toDollars()}"
}

@JvmInline
value class EUR(val cents: Long) {
    constructor(euros: Double) : this((euros * 100).toLong())

    fun toEuros(): Double = cents / 100.0

    operator fun plus(other: EUR): EUR = EUR(cents + other.cents)
    operator fun minus(other: EUR): EUR = EUR(cents - other.cents)

    override fun toString(): String = "€${toEuros()}"
}

// Usage - can't accidentally mix currencies
fun processPayment(amount: USD) {
    println("Processing payment: $amount")
}

val priceUSD = USD(99.99)
val priceEUR = EUR(89.99)

processPayment(priceUSD)  // 
// processPayment(priceEUR)  //  Compile error

val total = priceUSD + USD(10.0)  //  Type-safe
val discounted = priceUSD - USD(5.0)
```

---

#### 4. Timestamps and Durations

```kotlin
@JvmInline
value class Milliseconds(val value: Long) {
    fun toSeconds(): Seconds = Seconds(value / 1000)
}

@JvmInline
value class Seconds(val value: Long) {
    fun toMilliseconds(): Milliseconds = Milliseconds(value * 1000)
    fun toMinutes(): Minutes = Minutes(value / 60)
}

@JvmInline
value class Minutes(val value: Long) {
    fun toSeconds(): Seconds = Seconds(value * 60)
}

@JvmInline
value class UnixTimestamp(val value: Long) {
    fun toDate(): Date = Date(value)

    fun isAfter(other: UnixTimestamp): Boolean = value > other.value

    companion object {
        fun now(): UnixTimestamp = UnixTimestamp(System.currentTimeMillis())
    }
}

// Usage
fun cacheData(key: String, data: String, ttl: Seconds) {
    val expiresAt = UnixTimestamp.now().value + ttl.toMilliseconds().value
    // Store with expiration
}

cacheData("user:123", "data", Seconds(3600))  // 1 hour TTL
```

---

### VALUE CLASSES WITH INTERFACES

```kotlin
interface Identifier {
    val value: String
}

@JvmInline
value class UserId(override val value: String) : Identifier

@JvmInline
value class ProductId(override val value: String) : Identifier

fun logAccess(id: Identifier) {
    println("Accessing resource: ${id.value}")
}

// Usage
val userId = UserId("user123")
val productId = ProductId("product456")

logAccess(userId)     // Boxing occurs here 
logAccess(productId)  // Boxing occurs here 

// When used as interface type, value class is boxed
```

---

### ANDROID-SPECIFIC USE CASES

#### Resource IDs

```kotlin
@JvmInline
value class StringRes(@StringRes val value: Int)

@JvmInline
value class DrawableRes(@DrawableRes val value: Int)

@JvmInline
value class ColorRes(@ColorRes val value: Int)

@Composable
fun getText(stringRes: StringRes): String {
    return stringResource(id = stringRes.value)
}

@Composable
fun DisplayMessage() {
    val message = getText(StringRes(R.string.app_name))
    Text(text = message)
}
```

---

#### Navigation Arguments

```kotlin
@JvmInline
value class UserId(val value: String)

@JvmInline
value class PostId(val value: String)

sealed class Screen {
    data object Home : Screen()
    data class Profile(val userId: UserId) : Screen()
    data class PostDetail(val postId: PostId) : Screen()
}

fun NavController.navigate(screen: Screen) {
    when (screen) {
        is Screen.Home -> navigate("home")
        is Screen.Profile -> navigate("profile/${screen.userId.value}")
        is Screen.PostDetail -> navigate("post/${screen.postId.value}")
    }
}

// Usage - type-safe navigation
navController.navigate(Screen.Profile(UserId("user123")))
navController.navigate(Screen.PostDetail(PostId("post456")))
```

---

### LIMITATIONS AND BOXING

```kotlin
// Value classes are inlined, but boxing occurs in some cases:

@JvmInline
value class UserId(val value: String)

// 1. When used as Any
val userId = UserId("123")
val any: Any = userId  // Boxing occurs 

// 2. When used in collections
val list: List<UserId> = listOf(UserId("1"), UserId("2"))  // Boxing occurs 

// 3. When used as interface type
interface Identifier {
    val value: String
}
@JvmInline
value class UserId2(override val value: String) : Identifier
val id: Identifier = UserId2("123")  // Boxing occurs 

// 4. When used as nullable
val nullableId: UserId? = UserId("123")  // Boxing occurs 

// 5. Varargs
fun log(vararg ids: UserId) {  // Boxing occurs 
    ids.forEach { println(it.value) }
}

// To avoid boxing:
// - Use value classes directly (not as Any/interface)
// - Avoid nullable value classes when possible
// - Consider using regular classes for collections
```

---

### VALUE CLASSES IN SERIALIZATION

```kotlin
@Serializable
@JvmInline
value class UserId(val value: String)

@Serializable
data class User(
    val id: UserId,
    val name: String,
    val email: Email
)

// JSON serialization
val json = Json.encodeToString(
    User(
        id = UserId("user123"),
        name = "John Doe",
        email = Email("john@example.com")
    )
)

// Output: {"id":"user123","name":"John Doe","email":"john@example.com"}
// Value classes are serialized as their underlying values 
```

---

### BEST PRACTICES

```kotlin
//  Good: Single primitive property
@JvmInline
value class UserId(val value: String)

//  Bad: Multiple properties not allowed
// @JvmInline
// value class User(val id: String, val name: String)  // Won't compile

//  Good: Validation in init
@JvmInline
value class PositiveInt(val value: Int) {
    init {
        require(value > 0) { "Value must be positive" }
    }
}

//  Good: Extension functions for operations
@JvmInline
value class Percentage(val value: Double) {
    init {
        require(value in 0.0..100.0) { "Percentage must be 0-100" }
    }
}

fun Percentage.toDecimal(): Double = value / 100.0

//  Good: Companion object for factory methods
@JvmInline
value class Email(val value: String) {
    companion object {
        fun fromStringOrNull(str: String): Email? {
            return if (str.contains("@")) Email(str) else null
        }
    }
}
```

---

### KEY TAKEAWAYS

1. **Value classes** provide zero-overhead type-safe wrappers
2. **@JvmInline** annotation required for JVM targets
3. **Single val property** in primary constructor only
4. **No runtime overhead** when used directly
5. **Boxing occurs** when used as Any, in collections, nullable, interfaces
6. **Perfect for** IDs, measurements, money, timestamps
7. **Validation** in init block ensures invariants
8. **Serialization** treats value classes as underlying type
9. **Type safety** prevents mixing up similar primitive values
10. **Better than typealias** - actual type checking, not just alias

---

### Подробный ответ

---

### ОСНОВЫ VALUE КЛАССОВ

**Определение:**
```kotlin
@JvmInline
value class UserId(val value: String)

@JvmInline
value class Email(val value: String)

@JvmInline
value class Amount(val value: Double)

// Использование - типобезопасность без накладных расходов во время выполнения
fun getUser(userId: UserId): User {
    // Нельзя случайно передать сюда Email
    return userRepository.findById(userId.value)
}

fun sendEmail(email: Email, subject: String) {
    // Типобезопасная обработка email
}

val userId = UserId("user123")
val email = Email("user@example.com")

// Ошибка компиляции
// getUser(email)  // Несоответствие типов
```

**Ключевые особенности:**
```
 Нулевые накладные расходы во время выполнения (инлайнятся во время компиляции)
 Типобезопасность во время компиляции
 Должен иметь одно свойство в первичном конструкторе
 Свойство должно быть неизменяемым (val, не var)
 Заменяет inline классы (устарели в Kotlin 1.5)
 Требуется аннотация @JvmInline
```

---

### VALUE КЛАСС VS DATA КЛАСС

```kotlin
// Data класс - обычное выделение объекта
data class UserIdData(val value: String)

// Value класс - нет выделения объекта
@JvmInline
value class UserIdValue(val value: String)

// Сравнение производительности
fun testPerformance() {
    // Data класс: выделяет объект в куче
    val dataId = UserIdData("123")  // Выделение в куче

    // Value класс: нет выделения, инлайнится в String
    val valueId = UserIdValue("123")  // Нет выделения

    // Во время выполнения valueId - это просто "123"
}

// Использование памяти:
// Data класс: Заголовок объекта + ссылка на String = ~16 байт
// Value класс: Просто String = 0 дополнительных байт
```

---

### ТИПОБЕЗОПАСНЫЕ ДОМЕННЫЕ МОДЕЛИ

```kotlin
// Проблема: одержимость примитивами
fun createOrder(
    customerId: String,
    productId: String,
    quantity: Int,
    price: Double
) {
    // Легко перепутать параметры
    // createOrder("product123", "customer456", 10, 99.99)
}

// Решение: value классы
@JvmInline
value class CustomerId(val value: String)

@JvmInline
value class ProductId(val value: String)

@JvmInline
value class Quantity(val value: Int) {
    init {
        require(value > 0) { "Количество должно быть положительным" }
    }
}

@JvmInline
value class Price(val value: Double) {
    init {
        require(value >= 0) { "Цена должна быть неотрицательной" }
    }
}

fun createOrder(
    customerId: CustomerId,
    productId: ProductId,
    quantity: Quantity,
    price: Price
) {
    // Невозможно перепутать параметры
    // Типобезопасно и самодокументируемо
}

// Использование
val order = createOrder(
    customerId = CustomerId("customer456"),
    productId = ProductId("product123"),
    quantity = Quantity(10),
    price = Price(99.99)
)
```

---

### ВАЛИДАЦИЯ В VALUE КЛАССАХ

```kotlin
@JvmInline
value class Email(val value: String) {
    init {
        require(value.contains("@")) { "Неверный формат email" }
        require(value.length <= 100) { "Email слишком длинный" }
    }

    fun domain(): String = value.substringAfter("@")
    fun localPart(): String = value.substringBefore("@")
}

@JvmInline
value class PhoneNumber(val value: String) {
    init {
        val digits = value.filter { it.isDigit() }
        require(digits.length in 10..15) { "Неверный номер телефона" }
    }

    fun formatted(): String {
        val digits = value.filter { it.isDigit() }
        return when (digits.length) {
            10 -> "${digits.substring(0, 3)}-${digits.substring(3, 6)}-${digits.substring(6)}"
            11 -> "+${digits[0]} ${digits.substring(1, 4)}-${digits.substring(4, 7)}-${digits.substring(7)}"
            else -> value
        }
    }
}

@JvmInline
value class Password(val value: String) {
    init {
        require(value.length >= 8) { "Пароль должен быть не менее 8 символов" }
        require(value.any { it.isUpperCase() }) { "Пароль должен содержать заглавную букву" }
        require(value.any { it.isDigit() }) { "Пароль должен содержать цифру" }
    }

    fun strength(): PasswordStrength {
        return when {
            value.length >= 12 && value.any { !it.isLetterOrDigit() } -> PasswordStrength.STRONG
            value.length >= 10 -> PasswordStrength.MEDIUM
            else -> PasswordStrength.WEAK
        }
    }
}

enum class PasswordStrength { WEAK, MEDIUM, STRONG }

// Использование
try {
    val email = Email("user@example.com")
    val phone = PhoneNumber("1234567890")
    val password = Password("SecurePass123")

    println("Домен email: ${email.domain()}")
    println("Отформатированный телефон: ${phone.formatted()}")
    println("Надежность пароля: ${password.strength()}")
} catch (e: IllegalArgumentException) {
    println("Ошибка валидации: ${e.message}")
}
```

---

### РАСПРОСТРАНЕННЫЕ СЛУЧАИ ИСПОЛЬЗОВАНИЯ

#### 1. ID и идентификаторы

```kotlin
@JvmInline
value class UserId(val value: String)

@JvmInline
value class OrderId(val value: Long)

@JvmInline
value class SessionToken(val value: String) {
    fun isExpired(): Boolean {
        // Проверка истечения срока действия токена
        return false
    }
}

class UserRepository {
    private val users = mutableMapOf<UserId, User>()

    fun findById(id: UserId): User? = users[id]

    fun save(user: User) {
        users[user.id] = user
    }
}

data class User(
    val id: UserId,
    val email: Email,
    val name: String
)
```

---

#### 2. Измерения и единицы

```kotlin
@JvmInline
value class Meters(val value: Double) {
    fun toKilometers(): Kilometers = Kilometers(value / 1000)
    fun toMiles(): Miles = Miles(value * 0.000621371)
}

@JvmInline
value class Kilometers(val value: Double) {
    fun toMeters(): Meters = Meters(value * 1000)
}

@JvmInline
value class Miles(val value: Double) {
    fun toMeters(): Meters = Meters(value * 1609.344)
}

@JvmInline
value class Kilograms(val value: Double) {
    fun toPounds(): Pounds = Pounds(value * 2.20462)
}

@JvmInline
value class Pounds(val value: Double) {
    fun toKilograms(): Kilograms = Kilograms(value / 2.20462)
}

// Использование - невозможно перепутать единицы
fun calculateShippingCost(distance: Kilometers, weight: Kilograms): Price {
    val distanceInMiles = distance.toMeters().toMiles()
    val weightInPounds = weight.toPounds()

    val cost = distanceInMiles.value * 0.5 + weightInPounds.value * 0.1
    return Price(cost)
}

val distance = Kilometers(100.0)
val weight = Kilograms(5.0)
val cost = calculateShippingCost(distance, weight)
```

---

#### 3. Деньги и валюта

```kotlin
@JvmInline
value class USD(val cents: Long) {
    constructor(dollars: Double) : this((dollars * 100).toLong())

    fun toDollars(): Double = cents / 100.0

    operator fun plus(other: USD): USD = USD(cents + other.cents)
    operator fun minus(other: USD): USD = USD(cents - other.cents)
    operator fun times(multiplier: Int): USD = USD(cents * multiplier)
    operator fun div(divisor: Int): USD = USD(cents / divisor)

    override fun toString(): String = "$${toDollars()}"
}

@JvmInline
value class EUR(val cents: Long) {
    constructor(euros: Double) : this((euros * 100).toLong())

    fun toEuros(): Double = cents / 100.0

    operator fun plus(other: EUR): EUR = EUR(cents + other.cents)
    operator fun minus(other: EUR): EUR = EUR(cents - other.cents)

    override fun toString(): String = "€${toEuros()}"
}

// Использование - нельзя случайно смешать валюты
fun processPayment(amount: USD) {
    println("Обработка платежа: $amount")
}

val priceUSD = USD(99.99)
val priceEUR = EUR(89.99)

processPayment(priceUSD)  // 
// processPayment(priceEUR)  // Ошибка компиляции

val total = priceUSD + USD(10.0)  // Типобезопасно
val discounted = priceUSD - USD(5.0)
```

---

#### 4. Временные метки и длительность

```kotlin
@JvmInline
value class Milliseconds(val value: Long) {
    fun toSeconds(): Seconds = Seconds(value / 1000)
}

@JvmInline
value class Seconds(val value: Long) {
    fun toMilliseconds(): Milliseconds = Milliseconds(value * 1000)
    fun toMinutes(): Minutes = Minutes(value / 60)
}

@JvmInline
value class Minutes(val value: Long) {
    fun toSeconds(): Seconds = Seconds(value * 60)
}

@JvmInline
value class UnixTimestamp(val value: Long) {
    fun toDate(): Date = Date(value)

    fun isAfter(other: UnixTimestamp): Boolean = value > other.value

    companion object {
        fun now(): UnixTimestamp = UnixTimestamp(System.currentTimeMillis())
    }
}

// Использование
fun cacheData(key: String, data: String, ttl: Seconds) {
    val expiresAt = UnixTimestamp.now().value + ttl.toMilliseconds().value
    // Сохранить с истечением срока
}

cacheData("user:123", "data", Seconds(3600))  // TTL 1 час
```

---

### VALUE КЛАССЫ С ИНТЕРФЕЙСАМИ

```kotlin
interface Identifier {
    val value: String
}

@JvmInline
value class UserId(override val value: String) : Identifier

@JvmInline
value class ProductId(override val value: String) : Identifier

fun logAccess(id: Identifier) {
    println("Доступ к ресурсу: ${id.value}")
}

// Использование
val userId = UserId("user123")
val productId = ProductId("product456")

logAccess(userId)     // Происходит боксинг
logAccess(productId)  // Происходит боксинг

// При использовании в качестве типа интерфейса value класс упаковывается (boxing)
```

---

### СПЕЦИФИЧНЫЕ ДЛЯ ANDROID СЛУЧАИ ИСПОЛЬЗОВАНИЯ

#### ID ресурсов

```kotlin
@JvmInline
value class StringRes(@StringRes val value: Int)

@JvmInline
value class DrawableRes(@DrawableRes val value: Int)

@JvmInline
value class ColorRes(@ColorRes val value: Int)

@Composable
fun getText(stringRes: StringRes): String {
    return stringResource(id = stringRes.value)
}

@Composable
fun DisplayMessage() {
    val message = getText(StringRes(R.string.app_name))
    Text(text = message)
}
```

---

#### Аргументы навигации

```kotlin
@JvmInline
value class UserId(val value: String)

@JvmInline
value class PostId(val value: String)

sealed class Screen {
    data object Home : Screen()
    data class Profile(val userId: UserId) : Screen()
    data class PostDetail(val postId: PostId) : Screen()
}

fun NavController.navigate(screen: Screen) {
    when (screen) {
        is Screen.Home -> navigate("home")
        is Screen.Profile -> navigate("profile/${screen.userId.value}")
        is Screen.PostDetail -> navigate("post/${screen.postId.value}")
    }
}

// Использование - типобезопасная навигация
navController.navigate(Screen.Profile(UserId("user123")))
navController.navigate(Screen.PostDetail(PostId("post456")))
```

---

### ОГРАНИЧЕНИЯ И БОКСИНГ

```kotlin
// Value классы инлайнятся, но в некоторых случаях происходит боксинг:

@JvmInline
value class UserId(val value: String)

// 1. При использовании как Any
val userId = UserId("123")
val any: Any = userId  // Происходит боксинг

// 2. При использовании в коллекциях
val list: List<UserId> = listOf(UserId("1"), UserId("2"))  // Происходит боксинг

// 3. При использовании как тип интерфейса
interface Identifier {
    val value: String
}
@JvmInline
value class UserId2(override val value: String) : Identifier
val id: Identifier = UserId2("123")  // Происходит боксинг

// 4. При использовании как nullable
val nullableId: UserId? = UserId("123")  // Происходит боксинг

// 5. Varargs
fun log(vararg ids: UserId) {  // Происходит боксинг
    ids.forEach { println(it.value) }
}

// Чтобы избежать боксинга:
// - Используйте value классы напрямую (не как Any/интерфейс)
// - Избегайте nullable value классов, когда это возможно
// - Рассмотрите использование обычных классов для коллекций
```

---

### VALUE КЛАССЫ В СЕРИАЛИЗАЦИИ

```kotlin
@Serializable
@JvmInline
value class UserId(val value: String)

@Serializable
data class User(
    val id: UserId,
    val name: String,
    val email: Email
)

// Сериализация в JSON
val json = Json.encodeToString(
    User(
        id = UserId("user123"),
        name = "John Doe",
        email = Email("john@example.com")
    )
)

// Вывод: {"id":"user123","name":"John Doe","email":"john@example.com"}
// Value классы сериализуются как их базовые значения
```

---

### ЛУЧШИЕ ПРАКТИКИ

```kotlin
//  Хорошо: Одно свойство-примитив
@JvmInline
value class UserId(val value: String)

//  Плохо: Несколько свойств не допускаются
// @JvmInline
// value class User(val id: String, val name: String)  // Не скомпилируется

//  Хорошо: Валидация в init
@JvmInline
value class PositiveInt(val value: Int) {
    init {
        require(value > 0) { "Значение должно быть положительным" }
    }
}

//  Хорошо: Функции-расширения для операций
@JvmInline
value class Percentage(val value: Double) {
    init {
        require(value in 0.0..100.0) { "Процент должен быть в диапазоне 0-100" }
    }
}

fun Percentage.toDecimal(): Double = value / 100.0

//  Хорошо: Companion object для фабричных методов
@JvmInline
value class Email(val value: String) {
    companion object {
        fun fromStringOrNull(str: String): Email? {
            return if (str.contains("@")) Email(str) else null
        }
    }
}
```

---

### КЛЮЧЕВЫЕ ВЫВОДЫ

1. **Value классы** обеспечивают типобезопасные обёртки без накладных расходов
2. **@JvmInline** аннотация обязательна для JVM платформ
3. **Только одно val свойство** в первичном конструкторе
4. **Нет накладных расходов во время выполнения** при прямом использовании
5. **Боксинг происходит** при использовании как Any, в коллекциях, nullable, интерфейсах
6. **Идеально для** ID, измерений, денег, временных меток
7. **Валидация** в init блоке обеспечивает инварианты
8. **Сериализация** обрабатывает value классы как базовый тип
9. **Типобезопасность** предотвращает смешивание похожих примитивных значений
10. **Лучше чем typealias** - реальная проверка типов, а не просто псевдоним

## Follow-ups

1. What's the difference between value classes and inline classes?
2. How do value classes affect binary compatibility?
3. When should you use value classes vs data classes?
4. How do you use value classes with Retrofit?
5. What are the performance benchmarks for value classes?
6. How do value classes work with reflection?
7. Can you have secondary constructors in value classes?
8. How do you test code with value classes?
9. What happens when value class is used as generic parameter?
10. How do value classes interact with Compose remember and derivedStateOf?

## Related Questions

- [[q-api-file-upload-server--android--medium]]
- [[q-until-what-point-does-viewmodel-guarantee-state-preservation--android--medium]]
- [[q-kmm-ktor-networking--multiplatform--medium]]

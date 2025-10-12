---
topic: kotlin
tags:
  - kotlin
  - type-aliases
  - inline-classes
  - type-safety
  - performance
difficulty: medium
status: draft
---

# Type Aliases vs Inline Classes vs Wrapper Classes

**English**: When should you use type aliases vs inline classes vs wrapper classes? Compare memory overhead and type safety.

**Russian**: Когда использовать type aliases vs inline classes vs wrapper classes? Сравните memory overhead и type safety.

## Answer (EN)

Kotlin provides three ways to create type abstractions: type aliases, inline classes (value classes), and wrapper classes. Each has different trade-offs.

### Type Aliases - Compile-Time Only

**Purpose**: Create alternative names for existing types. No runtime overhead, no type safety.

```kotlin
// Type alias
typealias UserId = String
typealias Email = String
typealias ProductId = Int

fun getUser(id: UserId): User { ... }
fun sendEmail(email: Email) { ... }
fun getProduct(id: ProductId): Product { ... }

// Problem: No type safety at runtime!
val userId: UserId = "user123"
val email: Email = "user@example.com"

sendEmail(userId)  // ✅ Compiles! Type aliases don't provide safety
getUser(email)     // ✅ Compiles! They're all just String
```

**Characteristics**:
- Zero runtime overhead
- No type safety (just aliases)
- Useful for complex generic types
- Improves readability

**Good use cases**:
```kotlin
// Complex generic types
typealias StringMap = Map<String, String>
typealias Callback<T> = (T) -> Unit
typealias Predicate<T> = (T) -> Boolean

// Function types
typealias ClickListener = (View) -> Unit
typealias Validator = (String) -> Boolean

// Collections
typealias UserList = List<User>
typealias ErrorHandler = (Exception) -> Unit
```

### Inline Classes (Value Classes) - Type Safety with Zero Overhead

**Purpose**: Wrap a single value with type safety and zero runtime cost.

```kotlin
@JvmInline
value class UserId(val value: String)

@JvmInline
value class Email(val value: String)

@JvmInline
value class ProductId(val value: Int)

fun getUser(id: UserId): User { ... }
fun sendEmail(email: Email) { ... }

// Type safety!
val userId = UserId("user123")
val email = Email("user@example.com")

sendEmail(userId)  // ❌ Compile error! Type mismatch
getUser(email)     // ❌ Compile error! Type mismatch
```

**Characteristics**:
- Strong type safety at compile time
- Zero runtime overhead (inlined)
- Must wrap single value
- Can have methods and properties

**Advanced usage**:
```kotlin
@JvmInline
value class Password(private val value: String) {
    init {
        require(value.length >= 8) { "Password too short" }
    }

    fun validate(): Boolean {
        return value.any { it.isUpperCase() } &&
               value.any { it.isDigit() }
    }

    // Cannot expose wrapped value (security)
    override fun toString() = "***"
}

@JvmInline
value class Percentage(val value: Double) {
    init {
        require(value in 0.0..100.0) { "Invalid percentage" }
    }

    operator fun plus(other: Percentage) =
        Percentage((value + other.value).coerceAtMost(100.0))

    fun format() = "$value%"
}
```

**When inlining happens**:
```kotlin
@JvmInline
value class UserId(val value: String)

fun process(id: UserId) {
    println(id.value)
}

// Compiled to:
// fun process(id: String) {  // Inlined!
//     println(id)
// }
```

**When boxing occurs**:
```kotlin
@JvmInline
value class UserId(val value: String)

interface UserRepository {
    fun getUser(id: UserId): User  // Boxed!
}

val list: List<UserId> = listOf()  // Boxed!
val any: Any = UserId("123")       // Boxed!
```

### Wrapper Classes - Full OOP with Overhead

**Purpose**: Create distinct types with full OOP features but with runtime overhead.

```kotlin
// Regular wrapper class
data class UserId(val value: String) {
    init {
        require(value.isNotBlank()) { "UserId cannot be blank" }
    }

    fun toInt() = value.hashCode()
}

data class Email(val value: String) {
    val domain: String get() = value.substringAfter('@')

    init {
        require('@' in value) { "Invalid email" }
    }

    fun isGmail() = domain == "gmail.com"
}
```

**Characteristics**:
- Full type safety
- Runtime object creation (heap allocation)
- Can have multiple properties
- Support inheritance
- Memory overhead

**When to use**:
```kotlin
// Complex types with multiple properties
data class Money(
    val amount: BigDecimal,
    val currency: Currency
) {
    operator fun plus(other: Money): Money {
        require(currency == other.currency)
        return Money(amount + other.amount, currency)
    }
}

// Types needing inheritance
abstract class Identifier(val value: String)
class UserId(value: String) : Identifier(value)
class ProductId(value: String) : Identifier(value)
```

### Performance Comparison

```kotlin
// Benchmark results (approximate)
// Type Alias: 0 ns (compile-time only)
// Inline Class: 0 ns (inlined)
// Wrapper Class: 10-50 ns (allocation + GC)

@Benchmark
fun typeAlias(): String {
    val id: UserId = "123"  // typealias UserId = String
    return id  // No overhead
}

@Benchmark
fun inlineClass(): String {
    val id = UserId("123")  // @JvmInline value class UserId(val value: String)
    return id.value  // Inlined, no overhead
}

@Benchmark
fun wrapperClass(): String {
    val id = UserIdWrapper("123")  // data class UserIdWrapper(val value: String)
    return id.value  // Heap allocation + access
}
```

### Memory Overhead Comparison

```kotlin
// Type Alias
typealias UserId = String
val id: UserId = "123"  // 40 bytes (String object)

// Inline Class
@JvmInline
value class UserId(val value: String)
val id = UserId("123")  // 40 bytes (String object, UserId inlined)

// Wrapper Class
data class UserId(val value: String)
val id = UserId("123")  // 40 bytes (String) + 16 bytes (UserId object) = 56 bytes
```

### Comparison Matrix

| Feature | Type Alias | Inline Class | Wrapper Class |
|---------|------------|--------------|---------------|
| **Type Safety** | None (compile-time name only) | Strong | Strong |
| **Runtime Overhead** | Zero | Zero (when inlined) | Object allocation |
| **Memory** | No overhead | No overhead | 16+ bytes per instance |
| **Methods** | No | Yes | Yes |
| **Inheritance** | No | No | Yes |
| **Multiple Properties** | No | No | Yes |
| **Nullability** | Depends on underlying type | Explicit | Explicit |
| **Boxing** | N/A | Sometimes (interfaces, collections) | Always an object |

### Use Case Decision Tree

```
Need type abstraction?
│
├─ Just for readability?
│  └─ Use TYPE ALIAS
│     (Complex generics, function types)
│
├─ Need type safety?
│  │
│  ├─ Single value wrapper?
│  │  └─ Use INLINE CLASS
│  │     (IDs, primitive wrappers, units)
│  │
│  └─ Multiple properties OR inheritance?
│     └─ Use WRAPPER CLASS
│        (Domain models, complex types)
```

### Real-World Examples

**Type Aliases**:
```kotlin
typealias Json = String
typealias Callback<T> = (Result<T>) -> Unit
typealias UsersMap = Map<UserId, User>

interface ApiService {
    suspend fun getData(): Json
    fun observeUsers(callback: Callback<UsersMap>)
}
```

**Inline Classes**:
```kotlin
@JvmInline
value class Meters(val value: Double) {
    operator fun plus(other: Meters) = Meters(value + other.value)
}

@JvmInline
value class Seconds(val value: Long)

@JvmInline
value class Speed(val metersPerSecond: Double) {
    constructor(meters: Meters, seconds: Seconds) : this(
        meters.value / seconds.value
    )
}

// Usage
val distance = Meters(100.0)
val time = Seconds(10)
val speed = Speed(distance, time)
```

**Wrapper Classes**:
```kotlin
data class Location(
    val latitude: Double,
    val longitude: Double
) {
    fun distanceTo(other: Location): Meters {
        // Calculate distance
    }
}

data class Address(
    val street: String,
    val city: String,
    val country: String,
    val location: Location?
)
```

### Limitations

**Type Alias Limitations**:
- No type safety
- Can't add methods
- Can't inherit or implement interfaces

**Inline Class Limitations**:
- Single property only (Kotlin 1.x)
- Boxing in certain contexts (interfaces, collections)
- Can't have lateinit or delegated properties
- Can't extend other classes

**Wrapper Class Limitations**:
- Runtime overhead
- Memory allocation
- GC pressure for frequently created objects

### Best Practices

1. **Use type aliases** for complex generic types and readability
2. **Use inline classes** for type-safe wrappers without overhead
3. **Use wrapper classes** when you need multiple properties or inheritance
4. **Prefer inline classes** over type aliases for IDs and units
5. **Be aware of boxing** with inline classes
6. **Profile performance** if creating many short-lived objects
7. **Use data classes** for wrapper classes to get equals/hashCode/toString
8. **Make inline class properties private** for encapsulation
9. **Add validation** in init blocks
10. **Document boxing behavior** for inline classes

## Ответ (RU)

Kotlin предоставляет три способа создания типовых абстракций.

### Type Aliases - Только compile-time

Создает альтернативные имена для существующих типов. Нет runtime overhead, нет type safety.

### Inline Classes - Type Safety без overhead

Оборачивает одно значение с type safety и нулевой runtime стоимостью.

### Wrapper Classes - Полный OOP с overhead

Создает отдельные типы с полными OOP возможностями но с runtime overhead.

### Матрица сравнения

| Функция | Type Alias | Inline Class | Wrapper Class |
|---------|------------|--------------|---------------|
| **Type Safety** | Нет | Сильная | Сильная |
| **Runtime Overhead** | Ноль | Ноль (при inlining) | Аллокация объекта |
| **Память** | Нет overhead | Нет overhead | 16+ байт на экземпляр |

[Полные примеры и дерево решений приведены в английском разделе]

### Лучшие практики

1. **Используйте type aliases** для сложных generic типов
2. **Используйте inline classes** для type-safe wrappers без overhead
3. **Используйте wrapper classes** когда нужно несколько свойств
4. **Предпочитайте inline classes** вместо type aliases для ID
5. **Знайте о boxing** с inline classes
6. **Профилируйте производительность**
7. **Используйте data classes** для wrapper classes
8. **Делайте свойства inline class private** для инкапсуляции
9. **Добавляйте валидацию** в init блоках
10. **Документируйте boxing поведение**

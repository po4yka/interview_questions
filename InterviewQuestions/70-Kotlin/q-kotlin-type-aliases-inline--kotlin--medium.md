---
id: kotlin-164
title: "Kotlin Type Aliases Inline / Type aliases и inline в Kotlin"
aliases: [Type Aliases, Inline Classes, Inline Functions, Type Aliases и inline]
topic: kotlin
subtopics: [type-system, inline-functions, performance]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-data-class-requirements--programming-languages--medium, q-actor-pattern--kotlin--hard, q-coroutine-resource-cleanup--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags:
  - kotlin
  - type-aliases
  - inline-classes
  - type-safety
  - performance
  - difficulty/medium
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

sendEmail(userId)  //  Compiles! Type aliases don't provide safety
getUser(email)     //  Compiles! They're all just String
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

sendEmail(userId)  //  Compile error! Type mismatch
getUser(email)     //  Compile error! Type mismatch
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

 Just for readability?
   Use TYPE ALIAS
     (Complex generics, function types)

 Need type safety?
  
   Single value wrapper?
     Use INLINE CLASS
       (IDs, primitive wrappers, units)
  
   Multiple properties OR inheritance?
      Use WRAPPER CLASS
        (Domain models, complex types)
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

Kotlin предоставляет три способа создания типовых абстракций: псевдонимы типов (type aliases), встроенные классы (inline classes) и классы-обертки (wrapper classes). Каждый имеет различные компромиссы.

### Type Aliases - Только compile-time

**Назначение**: Создание альтернативных имен для существующих типов. Нет runtime overhead, нет type safety.

```kotlin
// Псевдоним типа
typealias UserId = String
typealias Email = String
typealias ProductId = Int

fun getUser(id: UserId): User { ... }
fun sendEmail(email: Email) { ... }

// Проблема: Нет type safety во время выполнения!
val userId: UserId = "user123"
val email: Email = "user@example.com"

sendEmail(userId)  // Компилируется! Псевдонимы не обеспечивают безопасность
getUser(email)     // Компилируется! Они все просто String
```

**Характеристики**:
- Нулевой runtime overhead
- Нет type safety (только псевдонимы)
- Полезны для сложных generic типов
- Улучшают читаемость

**Хорошие примеры использования**:
```kotlin
// Сложные generic типы
typealias StringMap = Map<String, String>
typealias Callback<T> = (T) -> Unit
typealias Predicate<T> = (T) -> Boolean

// Типы функций
typealias ClickListener = (View) -> Unit
typealias Validator = (String) -> Boolean
```

### Inline Classes (Value Classes) - Type Safety без overhead

**Назначение**: Оборачивает одно значение с type safety и нулевой runtime стоимостью.

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

sendEmail(userId)  // Ошибка компиляции! Несоответствие типов
getUser(email)     // Ошибка компиляции! Несоответствие типов
```

**Характеристики**:
- Строгая type safety во время компиляции
- Нулевой runtime overhead (inlined)
- Должен оборачивать одно значение
- Может иметь методы и свойства

**Продвинутое использование**:
```kotlin
@JvmInline
value class Password(private val value: String) {
    init {
        require(value.length >= 8) { "Пароль слишком короткий" }
    }

    fun validate(): Boolean {
        return value.any { it.isUpperCase() } &&
               value.any { it.isDigit() }
    }

    // Нельзя открыть обернутое значение (безопасность)
    override fun toString() = "***"
}

@JvmInline
value class Percentage(val value: Double) {
    init {
        require(value in 0.0..100.0) { "Неверный процент" }
    }

    operator fun plus(other: Percentage) =
        Percentage((value + other.value).coerceAtMost(100.0))

    fun format() = "$value%"
}
```

**Когда происходит inlining**:
```kotlin
@JvmInline
value class UserId(val value: String)

fun process(id: UserId) {
    println(id.value)
}

// Компилируется в:
// fun process(id: String) {  // Встроено!
//     println(id)
// }
```

**Когда происходит boxing**:
```kotlin
@JvmInline
value class UserId(val value: String)

interface UserRepository {
    fun getUser(id: UserId): User  // Boxing!
}

val list: List<UserId> = listOf()  // Boxing!
val any: Any = UserId("123")       // Boxing!
```

### Wrapper Classes - Полный OOP с overhead

**Назначение**: Создание отдельных типов с полными OOP возможностями но с runtime overhead.

```kotlin
// Обычный класс-обертка
data class UserId(val value: String) {
    init {
        require(value.isNotBlank()) { "UserId не может быть пустым" }
    }

    fun toInt() = value.hashCode()
}

data class Email(val value: String) {
    val domain: String get() = value.substringAfter('@')

    init {
        require('@' in value) { "Неверный email" }
    }

    fun isGmail() = domain == "gmail.com"
}
```

**Характеристики**:
- Полная type safety
- Runtime создание объектов (heap allocation)
- Может иметь несколько свойств
- Поддержка наследования
- Memory overhead

**Когда использовать**:
```kotlin
// Сложные типы с несколькими свойствами
data class Money(
    val amount: BigDecimal,
    val currency: Currency
) {
    operator fun plus(other: Money): Money {
        require(currency == other.currency)
        return Money(amount + other.amount, currency)
    }
}

// Типы, требующие наследования
abstract class Identifier(val value: String)
class UserId(value: String) : Identifier(value)
class ProductId(value: String) : Identifier(value)
```

### Сравнение производительности

```kotlin
// Результаты бенчмарков (приблизительно)
// Type Alias: 0 нс (только compile-time)
// Inline Class: 0 нс (inlined)
// Wrapper Class: 10-50 нс (аллокация + GC)

@Benchmark
fun typeAlias(): String {
    val id: UserId = "123"  // typealias UserId = String
    return id  // Нет overhead
}

@Benchmark
fun inlineClass(): String {
    val id = UserId("123")  // @JvmInline value class UserId(val value: String)
    return id.value  // Встроено, нет overhead
}

@Benchmark
fun wrapperClass(): String {
    val id = UserIdWrapper("123")  // data class UserIdWrapper(val value: String)
    return id.value  // Heap allocation + доступ
}
```

### Сравнение затрат памяти

```kotlin
// Type Alias
typealias UserId = String
val id: UserId = "123"  // 40 байт (объект String)

// Inline Class
@JvmInline
value class UserId(val value: String)
val id = UserId("123")  // 40 байт (объект String, UserId встроен)

// Wrapper Class
data class UserId(val value: String)
val id = UserId("123")  // 40 байт (String) + 16 байт (объект UserId) = 56 байт
```

### Матрица сравнения

| Функция | Type Alias | Inline Class | Wrapper Class |
|---------|------------|--------------|---------------|
| **Type Safety** | Нет (только compile-time имя) | Сильная | Сильная |
| **Runtime Overhead** | Ноль | Ноль (при inlining) | Аллокация объекта |
| **Память** | Нет overhead | Нет overhead | 16+ байт на экземпляр |
| **Методы** | Нет | Да | Да |
| **Наследование** | Нет | Нет | Да |
| **Несколько свойств** | Нет | Нет | Да |
| **Nullable** | Зависит от базового типа | Явно | Явно |
| **Boxing** | Н/Д | Иногда (интерфейсы, коллекции) | Всегда объект |

### Дерево принятия решений

```
Нужна типовая абстракция?

 Только для читаемости?
   Используйте TYPE ALIAS
     (Сложные generic, типы функций)

 Нужна type safety?

   Обертка одного значения?
     Используйте INLINE CLASS
       (ID, обертки примитивов, единицы измерения)

   Несколько свойств ИЛИ наследование?
      Используйте WRAPPER CLASS
        (Доменные модели, сложные типы)
```

### Примеры из реальной жизни

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

// Использование
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
        // Вычислить расстояние
    }
}

data class Address(
    val street: String,
    val city: String,
    val country: String,
    val location: Location?
)
```

### Ограничения

**Ограничения Type Alias**:
- Нет type safety
- Нельзя добавить методы
- Нельзя наследовать или реализовать интерфейсы

**Ограничения Inline Class**:
- Только одно свойство (Kotlin 1.x)
- Boxing в определенных контекстах (интерфейсы, коллекции)
- Нельзя иметь lateinit или делегированные свойства
- Нельзя расширять другие классы

**Ограничения Wrapper Class**:
- Runtime overhead
- Аллокация памяти
- Нагрузка на GC для часто создаваемых объектов

### Лучшие практики

1. **Используйте type aliases** для сложных generic типов и читаемости
2. **Используйте inline classes** для type-safe wrappers без overhead
3. **Используйте wrapper classes** когда нужно несколько свойств или наследование
4. **Предпочитайте inline classes** вместо type aliases для ID и единиц измерения
5. **Знайте о boxing** с inline classes
6. **Профилируйте производительность** если создаете много короткоживущих объектов
7. **Используйте data classes** для wrapper classes чтобы получить equals/hashCode/toString
8. **Делайте свойства inline class private** для инкапсуляции
9. **Добавляйте валидацию** в init блоках
10. **Документируйте boxing поведение** для inline classes

**Резюме**: Kotlin предоставляет три способа создания типовых абстракций с различными компромиссами. Type aliases предоставляют нулевой overhead но без type safety. Inline classes обеспечивают strong type safety без runtime overhead. Wrapper classes предоставляют полный OOP функционал с runtime overhead. Выбирайте type aliases для сложных типов, inline classes для безопасных оберток без overhead, и wrapper classes когда нужно несколько свойств или наследование.

## Related Questions

- [[q-data-class-requirements--programming-languages--medium]]
- [[q-actor-pattern--kotlin--hard]]
- [[q-coroutine-resource-cleanup--kotlin--medium]]

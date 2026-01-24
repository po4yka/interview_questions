---
'---id': kotlin-164
title: Kotlin Type Aliases Inline / Type aliases и inline в Kotlin
aliases:
- Inline Classes
- Inline Functions
- Type Aliases
- Type Aliases и inline
topic: kotlin
subtopics:
- inline-functions
- type-system
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-compose-recomposition
- c-kotlin
- c-perfetto
- c-power-profiling
- q-actor-pattern--kotlin--hard
- q-coroutine-resource-cleanup--kotlin--medium
created: 2025-10-15
updated: 2025-11-09
tags:
- difficulty/medium
- inline-classes
- kotlin
- performance
- type-aliases
- type-safety
anki_cards:
- slug: q-kotlin-type-aliases-inline--kotlin--medium-0-en
  language: en
  anki_id: 1768326283407
  synced_at: '2026-01-23T17:03:50.793935'
- slug: q-kotlin-type-aliases-inline--kotlin--medium-0-ru
  language: ru
  anki_id: 1768326283430
  synced_at: '2026-01-23T17:03:50.795094'
---
# Вопрос (RU)

> Когда использовать `typealias` (type aliases) vs `inline/value class` (inline classes) vs wrapper classes в Kotlin? Сравните memory overhead и type safety.

# Question (EN)

> When should you use `typealias` (type aliases) vs `inline/value class` (inline classes) vs wrapper classes in Kotlin? Compare memory overhead and type safety.

## Ответ (RU)

Kotlin предоставляет три способа создания типовых абстракций: псевдонимы типов (type aliases), встроенные/значимые классы (inline/value classes) и классы-обертки (wrapper classes). Каждый имеет свои компромиссы.

### Type Aliases - Только Compile-time

**Назначение**: Создание альтернативных имен для существующих типов. Нет дополнительного runtime overhead, не создают новый тип.

```kotlin
// Псевдоним типа
typealias UserId = String
typealias Email = String
typealias ProductId = Int

fun getUser(id: UserId): User { ... }
fun sendEmail(email: Email) { ... }
fun getProduct(id: ProductId): Product { ... }

// Проблема: псевдоним не создает отдельный тип
val userId: UserId = "user123"
val email: Email = "user@example.com"

sendEmail(userId)  // Компилируется: UserId это все тот же String
getUser(email)     // Компилируется: Email тоже просто String
```

**Характеристики**:
- Нулевой runtime overhead (чисто compile-time псевдоним)
- Не дают дополнительной type safety по сравнению с базовым типом
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

// Коллекции
typealias UserList = List<User>
typealias ErrorHandler = (Exception) -> Unit
```

### Inline Classes (Value Classes) - Type Safety С (часто) Нулевым overhead

**Назначение**: Обернуть одно значение, получив отдельный тип и позволяя компилятору/рантайму представлять его без дополнительного объекта во многих случаях.

```kotlin
@JvmInline
value class UserId(val value: String)

@JvmInline
value class Email(val value: String)

@JvmInline
value class ProductId(val value: Int)

fun getUser(id: UserId): User { ... }
fun sendEmail(email: Email): Unit { ... }

// Type safety между разными доменными понятиями
val userId = UserId("user123")
val email = Email("user@example.com")

sendEmail(userId)  // Ошибка компиляции: несоответствие типов
getUser(email)     // Ошибка компиляции: несоответствие типов
```

**Характеристики**:
- Более строгая type safety на уровне компиляции (отдельный тип)
- Во многих контекстах представляются без дополнительного объекта (зависит от backend и контекста)
- Должны оборачивать одно значение в primary-конструкторе
- Могут иметь методы и свойства

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

    // Избегаем утечки исходного значения (безопасность)
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

**Когда обычно происходит inlining (пример JVM)**:
```kotlin
@JvmInline
value class UserId(val value: String)

fun process(id: UserId) {
    println(id.value)
}

// Возможный вариант компиляции:
// fun process(id: String) {
//     println(id)
// }
```

**Когда происходит boxing (типичные случаи)**:
```kotlin
@JvmInline
value class UserId(val value: String)

interface UserRepository {
    fun getUser(id: UserId): User  // Может требовать boxing в зависимости от backend/контекста
}

val list: List<UserId> = listOf()  // Элементы UserId, как правило, боксируются
val any: Any = UserId("123")       // Boxing для хранения как Any
```

### Wrapper Classes - Полный OOP С overhead

**Назначение**: Создание отдельных типов с полными OOP-возможностями, которые всегда существуют как обычные объекты.

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
- Полная type safety (номинально отдельный тип)
- Runtime-создание объектов (аллокация на куче в JVM)
- Может иметь несколько свойств
- Поддержка наследования
- Дополнительные затраты памяти по сравнению с "сырым" значением

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

### Сравнение Производительности

```kotlin
// Приблизительное / иллюстративное поведение (конкретные числа зависят от JVM, компилятора, backend и т.д.)
// Type Alias: нет дополнительной работы (только compile-time)
// Inline/Value Class: часто без дополнительной аллокации при отсутствии boxing
// Wrapper Class: дополнительная аллокация + возможная работа GC

@Benchmark
fun typeAlias(): String {
    val id: UserId = "123"  // typealias UserId = String
    return id  // Нет overhead относительно обычного String
}

@Benchmark
fun inlineClass(): String {
    val id = UserId("123")  // @JvmInline value class UserId(val value: String)
    return id.value  // Может быть скомпилировано без доп. аллокации
}

@Benchmark
fun wrapperClass(): String {
    val id = UserIdWrapper("123")  // data class UserIdWrapper(val value: String)
    return id.value  // Требуется аллокация объекта
}
```

### Сравнение Затрат Памяти

```kotlin
// Следующие оценки иллюстративны для JVM и не являются гарантированными:

// Type Alias
typealias UserId = String
val id: UserId = "123"  // Использует ту же память, что и объект String

// Inline Class
@JvmInline
value class UserId(val value: String)
val id = UserId("123")  // Обычно только String в inlined-контекстах

// Wrapper Class
data class UserId(val value: String)
val id = UserId("123")  // Объект String + отдельный объект UserId
```

### Матрица Сравнения

| Функция | Type Alias | Inline Class (Value Class) | Wrapper Class |
|---------|------------|----------------------------|---------------|
| **Type Safety** | Нет нового типа (только псевдоним) | Сильная | Сильная |
| **Runtime Overhead** | Нет сверх базового типа | Часто нет при unboxed; есть при boxing | Всегда аллокация объекта |
| **Память** | Как у базового типа | Как у базового значения при unboxed | Доп. объект на экземпляр |
| **Методы** | Нет | Да | Да |
| **Наследование** | Нет | Нет | Да |
| **Несколько свойств** | Нет | Нет | Да |
| **Nullable** | Зависит от базового типа | Явно | Явно |
| **Boxing** | Н/Д | Иногда (интерфейсы, generics, Any и т.п.) | Всегда объект |

### Дерево Принятия Решений

```text
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

### Примеры Из Реальной Жизни

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
- Не создают отдельный тип, поэтому не предотвращают смешивание псевдонимов с одинаковым базовым типом
- Нельзя добавить методы
- Нельзя наследовать или реализовать интерфейсы

**Ограничения Inline Class (Value Class)**:
- Ровно одно свойство в primary-конструкторе
- Boxing в определенных контекстах (интерфейсы, generics, Any и т.п.)
- Нельзя иметь lateinit или делегированные свойства
- Нельзя расширять другие классы (но можно реализовывать интерфейсы)

**Ограничения Wrapper Class**:
- Runtime overhead
- Дополнительная аллокация памяти
- Нагрузка на GC для часто создаваемых объектов

### Лучшие Практики

1. Используйте type aliases для сложных generic типов и читаемости
2. Используйте inline/value classes для type-safe оберток при минимальном overhead
3. Используйте wrapper classes, когда нужны несколько свойств или наследование
4. Предпочитайте inline/value classes вместо type aliases для ID и единиц измерения, если это поддерживается вашими целевыми платформами
5. Учитывайте boxing для value classes и его влияние на производительность
6. Профилируйте производительность, если создаете много короткоживущих объектов
7. Используйте data classes для wrapper classes, чтобы получить equals/hashCode/toString
8. По возможности делайте внутреннее значение value class приватным для инкапсуляции
9. Добавляйте валидацию в init-блоках при необходимости
10. Документируйте поведение boxing и семантику value classes в кодовой базе, когда это существенно

**Резюме**: Kotlin предоставляет три способа создания типовых абстракций с различными компромиссами. Type aliases дают нулевой overhead, но не создают новый тип и не защищают от смешивания разных псевдонимов поверх одного базового типа. Inline/value classes обеспечивают отдельный тип и могут компилироваться без дополнительной аллокации, кроме случаев boxing. Wrapper classes предоставляют полный OOP-функционал ценой постоянного runtime overhead. Выбирайте type aliases для сложных типов и читаемости, inline/value classes для безопасных оберток с минимальными накладными расходами и wrapper classes, когда нужны несколько свойств, наследование или более сложное поведение.

## Answer (EN)

Kotlin provides three ways to create type abstractions: type aliases, inline classes (value classes), and wrapper classes. Each has different trade-offs.

### Type Aliases - Compile-Time Only

**Purpose**: Create alternative names for existing types. No additional runtime overhead, no new distinct type.

```kotlin
// Type alias
typealias UserId = String
typealias Email = String
typealias ProductId = Int

fun getUser(id: UserId): User { ... }
fun sendEmail(email: Email): Unit { ... }
fun getProduct(id: ProductId): Product { ... }

// Problem: Aliases do not create distinct types
val userId: UserId = "user123"
val email: Email = "user@example.com"

sendEmail(userId)  //  Compiles: UserId is still String under the hood
getUser(email)     //  Compiles: Email is also just String
```

**Characteristics**:
- Zero runtime overhead (purely compile-time alias)
- Do not provide additional type safety vs underlying type
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

### Inline Classes (Value Classes) - Type Safety with (Often) Zero Overhead

**Purpose**: Wrap a single value with type safety while allowing the compiler/JVM/JS/Native to represent it without an additional object in many cases.

```kotlin
@JvmInline
value class UserId(val value: String)

@JvmInline
value class Email(val value: String)

@JvmInline
value class ProductId(val value: Int)

fun getUser(id: UserId): User { ... }
fun sendEmail(email: Email): Unit { ... }

// Type safety between logically different concepts
val userId = UserId("user123")
val email = Email("user@example.com")

sendEmail(userId)  //  Compile error: type mismatch
getUser(email)     //  Compile error: type mismatch
```

**Characteristics**:
- Stronger type safety at compile time (distinct type)
- Can be represented without an extra object in many usages (inlined representation is backend- and context-dependent)
- Must wrap a single underlying value in the primary constructor
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

    // Avoid exposing raw value (security)
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

**When inlining typically happens (JVM example)**:
```kotlin
@JvmInline
value class UserId(val value: String)

fun process(id: UserId) {
    println(id.value)
}

// One possible compilation:
// fun process(id: String) {
//     println(id)
// }
```

**When boxing occurs (common cases)**:
```kotlin
@JvmInline
value class UserId(val value: String)

interface UserRepository {
    fun getUser(id: UserId): User  // May require boxing depending on backend/usage
}

val list: List<UserId> = listOf()  // UserId elements are typically boxed
val any: Any = UserId("123")       // Boxed to be stored as Any
```

### Wrapper Classes - Full OOP with Overhead

**Purpose**: Create distinct types with full OOP features, always as regular objects.

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
- Full type safety (distinct nominal type)
- Runtime object creation (heap allocation on JVM)
- Can have multiple properties
- Support inheritance
- Additional memory overhead vs bare underlying value

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
// Approximate / illustrative behavior (actual numbers depend on JVM, compiler, backend, etc.)
// Type Alias: no extra work (compile-time only)
// Inline/Value Class: often no extra allocation when not boxed
// Wrapper Class: extra allocation + possible GC work

@Benchmark
fun typeAlias(): String {
    val id: UserId = "123"  // typealias UserId = String
    return id  // No overhead vs plain String
}

@Benchmark
fun inlineClass(): String {
    val id = UserId("123")  // @JvmInline value class UserId(val value: String)
    return id.value  // Can be compiled without extra allocation
}

@Benchmark
fun wrapperClass(): String {
    val id = UserIdWrapper("123")  // data class UserIdWrapper(val value: String)
    return id.value  // Requires object allocation
}
```

### Memory Overhead Comparison

```kotlin
// The following sizes are illustrative for JVM and not guaranteed:

// Type Alias
typealias UserId = String
val id: UserId = "123"  // Same memory as String instance

// Inline Class
@JvmInline
value class UserId(val value: String)
val id = UserId("123")  // Typically just the String at runtime in inlined contexts

// Wrapper Class
data class UserId(val value: String)
val id = UserId("123")  // String object + separate UserId object
```

### Comparison Matrix

| Feature | Type Alias | Inline Class (Value Class) | Wrapper Class |
|---------|------------|----------------------------|---------------|
| **Type Safety** | No new type (just alias) | Strong | Strong |
| **Runtime Overhead** | None vs underlying type | Often none when unboxed; overhead when boxed | Always an object allocation |
| **Memory** | Same as underlying type | Same as underlying value when unboxed | Extra object per instance |
| **Methods** | No | Yes | Yes |
| **Inheritance** | No | No | Yes |
| **Multiple Properties** | No | No | Yes |
| **Nullability** | Depends on underlying type | Explicit | Explicit |
| **Boxing** | N/A | Sometimes (interfaces, generics, Any, etc.) | Always boxed object |

### Use Case Decision Tree

```text
Need type abstraction?

 Just for readability?
   Use TYPE ALIAS
     (Complex generics, function types)

 Need type safety?

   Single value wrapper?
     Use INLINE CLASS
       (IDs, primitive-like wrappers, units)

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
- No distinct type, so can't prevent mixing of aliases with the same underlying type
- Can't add methods
- Can't inherit or implement interfaces

**Inline Class (Value Class) Limitations**:
- Exactly one underlying property in the primary constructor
- Boxing in certain contexts (interfaces, generics, Any, etc.)
- Can't have lateinit or delegated properties
- Can't extend other classes (but can implement interfaces)

**Wrapper Class Limitations**:
- Runtime overhead
- Additional memory allocation
- GC pressure for frequently created objects

### Best Practices

1. Use type aliases for complex generic types and readability
2. Use inline/value classes for type-safe wrappers when you want minimal overhead
3. Use wrapper classes when you need multiple properties or inheritance
4. Prefer inline/value classes over type aliases for IDs and units when supported by your target platforms
5. Be aware of boxing with value classes and its performance impact
6. Profile performance if creating many short-lived objects
7. Use data classes for wrapper classes to get equals/hashCode/toString
8. Consider keeping value class underlying properties private when you need encapsulation
9. Add validation in init blocks where appropriate
10. Document boxing behavior and semantics for value classes in your codebase when it matters

**Summary**: Kotlin provides three mechanisms for type abstractions with different trade-offs. Type aliases give zero overhead but don't create new types and don't prevent mixing aliases with the same underlying type. Inline/value classes provide distinct types and can be compiled without extra allocations except when boxing is required. Wrapper classes offer full OOP capabilities at the cost of constant runtime overhead. Choose type aliases for complex types and readability, inline/value classes for safe, low-overhead wrappers, and wrapper classes when you need multiple properties, inheritance, or more complex behavior.

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этих механизмов от Java-подходов?
- Когда бы вы использовали каждый из этих вариантов на практике?
- Каковы распространенные подводные камни и ошибки при использовании этих подходов?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Связанные Вопросы (RU)

- [[q-actor-pattern--kotlin--hard]]
- [[q-coroutine-resource-cleanup--kotlin--medium]]

## Related Questions

- [[q-actor-pattern--kotlin--hard]]
- [[q-coroutine-resource-cleanup--kotlin--medium]]

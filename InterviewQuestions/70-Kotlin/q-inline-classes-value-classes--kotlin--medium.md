---
id: 20251005-235013
title: "Inline Classes (Value Classes) / Встроенные классы (Value классы)"
aliases: []

# Classification
topic: kotlin
subtopics: [inline-class, value-class, performance, optimization]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository - Kotlin Batch 2

# Workflow & relations
status: reviewed
moc: moc-kotlin
related: [q-type-aliases--kotlin--medium]

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [kotlin, inline-class, value-class, performance, optimization, difficulty/medium]
---
## Question (EN)
> What are inline classes (value classes) in Kotlin?
## Вопрос (RU)
> Что такое встроенные классы (value классы) в Kotlin?

---

## Answer (EN)

Inline classes (now called **value classes**) are a special kind of class that wraps another type without adding runtime overhead through additional heap allocations.

### Problem They Solve

Sometimes business logic requires wrapping a type, but this introduces performance overhead due to heap allocations, especially for primitives.

```kotlin
// Regular wrapper - creates heap objects
class UserId(val value: String)  // Heap allocation

// Every UserId creation allocates memory
val id = UserId("12345")  // Allocation!
```

### Solution: Value Classes

```kotlin
// Value class - NO heap allocation at runtime!
@JvmInline
value class UserId(val value: String)

// At runtime, this is just a String
val id = UserId("12345")  // No extra allocation!
```

### Syntax

```kotlin
// Modern syntax (Kotlin 1.5+)
@JvmInline
value class Password(val value: String)

// Old syntax (deprecated)
inline class Password(val value: String)
```

### Restrictions

- **Must have exactly one property** initialized in primary constructor
- **Cannot have init blocks**
- **Properties cannot have backing fields** (only computed properties)
- **No lateinit or delegated properties**
- **Cannot extend other classes** (must be final)
- **Can implement interfaces**

```kotlin
// - Valid
@JvmInline
value class Email(val value: String) {
    val domain: String  // Computed property - OK
        get() = value.substringAfter('@')

    fun isValid(): Boolean = value.contains('@')
}

// - Invalid
@JvmInline
value class Invalid(val value: String) {
    var count: Int = 0  // - Backing field not allowed

    init {  // - Init block not allowed
        println("Created")
    }

    lateinit var data: String  // - lateinit not allowed
}
```

### Value Classes vs Type Aliases

| Feature | Value Class | Type Alias |
|---------|-------------|------------|
| **Creates new type** | - Yes | - No (just a name) |
| **Type safety** | - Strong | - Weak |
| **Runtime overhead** | - None (inlined) | - None |
| **Can have members** | - Yes | - No |

```kotlin
// Type alias - no type safety
typealias EmailAlias = String
typealias PasswordAlias = String

val email: EmailAlias = "user@example.com"
val password: PasswordAlias = email  // - Compiles! No safety

// Value class - type safety
@JvmInline
value class Email(val value: String)
@JvmInline
value class Password(val value: String)

val email2 = Email("user@example.com")
val password2: Password = email2  // - Compilation error! Type safe
```

### Use Cases

#### 1. Type-Safe IDs

```kotlin
@JvmInline
value class UserId(val value: Int)

@JvmInline
value class ProductId(val value: Int)

fun getUser(id: UserId): User { /* ... */ }
fun getProduct(id: ProductId): Product { /* ... */ }

// Prevents mixing IDs
val userId = UserId(123)
val productId = ProductId(456)

getUser(userId)  // - OK
// getUser(productId)  // - Compilation error!
```

#### 2. Units of Measurement

```kotlin
@JvmInline
value class Meters(val value: Double) {
    operator fun plus(other: Meters) = Meters(value + other.value)
}

@JvmInline
value class Kilometers(val value: Double) {
    fun toMeters() = Meters(value * 1000)
}

val distance = Meters(100.0) + Meters(50.0)  // Type-safe
// val invalid = Meters(100.0) + Kilometers(1.0)  // - Error!
```

#### 3. Validated Strings

```kotlin
@JvmInline
value class Email private constructor(val value: String) {
    companion object {
        fun create(value: String): Email? {
            return if (value.contains('@')) Email(value) else null
        }
    }
}

// Can only create valid emails
val email = Email.create("user@example.com")  // Email?
val invalid = Email.create("not-an-email")  // null
```

### Performance

Value classes have **zero runtime overhead** in most cases:

```kotlin
@JvmInline
value class Password(val value: String)

fun hashPassword(password: Password): String {
    return password.value.hashCode().toString()
}

// At runtime, compiles to:
fun hashPassword(password: String): String {
    return password.hashCode().toString()
}
// No Password object created!
```

**English Summary**: Value classes (inline classes) wrap types without runtime overhead, providing type safety without performance cost. Must have single property in primary constructor. Cannot have backing fields, init blocks, or extend classes. Unlike type aliases which are just names, value classes create real distinct types. Use for type-safe IDs, units of measurement, and validated wrappers. Zero allocation at runtime.

## Ответ (RU)

Встроенные классы (теперь называются **value классы**) — это специальный вид классов, которые оборачивают другой тип без добавления overhead во время выполнения через дополнительные выделения памяти в куче.

### Проблема которую решают

Иногда бизнес-логика требует обертывания типа, но это вводит overhead из-за выделений в куче, особенно для примитивов.

### Решение: Value классы

```kotlin
// Value класс - НЕТ выделения в куче во время выполнения!
@JvmInline
value class UserId(val value: String)

// Во время выполнения это просто String
val id = UserId("12345")  // Нет дополнительного выделения!
```

### Ограничения

- **Должен иметь ровно одно свойство** в первичном конструкторе
- **Не может иметь init блоки**
- **Свойства не могут иметь backing fields** (только вычисляемые)
- **Не может расширять другие классы** (должен быть final)
- **Может реализовывать интерфейсы**

### Value классы vs псевдонимы типов

| Функция | Value класс | Псевдоним типа |
|---------|-------------|----------------|
| **Создает новый тип** | - Да | - Нет |
| **Типобезопасность** | - Сильная | - Слабая |
| **Runtime overhead** | - Нет | - Нет |
| **Может иметь члены** | - Да | - Нет |

### Производительность

Value классы имеют **нулевой runtime overhead** в большинстве случаев.

**Краткое содержание**: Value классы оборачивают типы без runtime overhead, обеспечивая типобезопасность без стоимости производительности. Должны иметь одно свойство в первичном конструкторе. Не могут иметь backing fields, init блоки или расширять классы. В отличие от псевдонимов типов которые просто имена, value классы создают реальные отдельные типы. Используйте для типобезопасных ID, единиц измерения и валидированных оберток. Нулевое выделение во время выполнения.

---

## References
- [Inline Classes - Kotlin Documentation](https://kotlinlang.org/docs/reference/inline-classes.html)

## Related Questions
- [[q-type-aliases--kotlin--medium]]

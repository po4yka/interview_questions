---
id: kotlin-018
title: "Inline Classes (Value Classes) / Встроенные классы (Value классы)"
aliases: ["Inline Classes (Value Classes)", "Встроенные классы (Value классы)"]

# Classification
topic: kotlin
subtopics: [optimization, performance]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: "https://github.com/Kirchhoff-/Android-Interview-Questions"
source_note: Kirchhoff Android Interview Questions repository - Kotlin Batch 2

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-kotlin, q-inline-value-classes-performance--kotlin--medium, q-kotlin-inline-functions--kotlin--medium]

# Timestamps
created: 2025-10-05
updated: 2025-11-09

tags: [difficulty/medium, kotlin, optimization, performance, value-class]
---
# Вопрос (RU)
> Что такое встроенные классы (value классы) в Kotlin?

---

# Question (EN)
> What are inline classes (value classes) in Kotlin?

## Ответ (RU)

Встроенные классы (теперь называются **value классы**) — это специальный вид классов, которые оборачивают другой тип и могут представляться как значение этого типа без создания отдельного объекта в большинстве случаев, что уменьшает overhead дополнительных выделений памяти.

### Проблема которую решают

Иногда бизнес-логика требует обертывания типа (например, ID, Email, единицы измерения), чтобы повысить типобезопасность и инкапсулировать логику, но обычные обертки создают дополнительные объекты и накладные расходы по памяти и времени.

```kotlin
// Обычный класс-обертка — создает объект в куче
class UserIdBox(val value: String)

val idBox = UserIdBox("12345")  // Выделение в куче
```

### Решение: value классы

```kotlin
// Value класс: в большинстве вызовов представляется как String без отдельного объекта
@JvmInline
value class UserId(val value: String)

// В типичных местах использования JVM-код оперирует непосредственно String
val id = UserId("12345")
```

Важно: при некоторых использованиях (nullable типы, generics, сохранение как Any и т.п.) value класс может быть упакован (boxed) в объект и тогда выделение все же произойдет.

### Синтаксис

```kotlin
// Актуальный синтаксис (Kotlin 1.5+)
@JvmInline
value class Password(val value: String)

// Старый синтаксис (deprecated)
inline class PasswordLegacy(val value: String)
```

### Ограничения

- Должен иметь ровно одно свойство, инициализируемое в первичном конструкторе
- Не может иметь init блоки
- Свойства не могут иметь backing fields (только вычисляемые свойства)
- Нельзя использовать lateinit или делегированные свойства
- Не может расширять другие классы (final)
- Может реализовывать интерфейсы

```kotlin
// Валидный пример
@JvmInline
value class Email(val value: String) {
    val domain: String
        get() = value.substringAfter('@')

    fun isValid(): Boolean = value.contains('@')
}

// Невалидный пример
@JvmInline
value class Invalid(val value: String) {
    var count: Int = 0  // Backing field не разрешен

    init {              // init блок не разрешен
        println("Created")
    }

    lateinit var data: String  // lateinit не разрешен
}
```

### Value классы vs псевдонимы типов

| Функция | Value класс | Псевдоним типа |
|--------|-------------|----------------|
| Создает новый тип | Да | Нет |
| Типобезопасность | Сильная | Слабая |
| Runtime overhead | Обычно отсутствует (кроме boxing-сценариев) | Нет |
| Может иметь члены | Да | Нет |

```kotlin
// Псевдоним типа — без дополнительной типобезопасности
typealias EmailAlias = String
typealias PasswordAlias = String

val emailAlias: EmailAlias = "user@example.com"
val passwordAlias: PasswordAlias = emailAlias  // Компилируется

// Value классы — разные типы
@JvmInline
value class EmailAddress(val value: String)
@JvmInline
value class PasswordValue(val value: String)

val email = EmailAddress("user@example.com")
// val password: PasswordValue = email  // Ошибка компиляции
```

### Сценарии использования

#### 1. Типобезопасные ID

```kotlin
@JvmInline
value class UserId(val value: Int)

@JvmInline
value class ProductId(val value: Int)

fun getUser(id: UserId): User { /* ... */ }
fun getProduct(id: ProductId): Product { /* ... */ }

// Предотвращает смешивание ID
val userId = UserId(123)
val productId = ProductId(456)

getUser(userId)  // OK
// getUser(productId)  // Ошибка компиляции!
```

#### 2. Единицы измерения

```kotlin
@JvmInline
value class Meters(val value: Double) {
    operator fun plus(other: Meters) = Meters(value + other.value)
}

@JvmInline
value class Kilometers(val value: Double) {
    fun toMeters() = Meters(value * 1000)
}

val distance = Meters(100.0) + Meters(50.0)  // Типобезопасно
// val invalid = Meters(100.0) + Kilometers(1.0)  // Ошибка!
```

#### 3. Валидированные строки

```kotlin
@JvmInline
value class EmailValue private constructor(val value: String) {
    companion object {
        fun create(value: String): EmailValue? {
            return if (value.contains('@')) EmailValue(value) else null
        }
    }
}

// Можно создавать только валидные email-адреса
val emailValue = EmailValue.create("user@example.com")  // EmailValue?
val invalidEmail = EmailValue.create("not-an-email")  // null
```

### Производительность

Value классы спроектированы так, чтобы предоставлять типобезопасность с минимальным или нулевым runtime overhead в типичных сценариях. При использовании как не-nullable конкретных типов компилятор часто представляет их непосредственно базовым типом (без объекта-обертки). Когда необходим boxing (nullable value класс, использование в обобщениях, хранение как Any и т.п.), создается объект.

```kotlin
@JvmInline
value class Password(val value: String)

fun hashPassword(password: Password): String {
    return password.value.hashCode().toString()
}

// На JVM это может быть скомпилировано эквивалентно:
fun hashPassword(value: String): String {
    return value.hashCode().toString()
}
// В этом сценарии объект Password создавать не нужно.
```

Кратко: value классы (inline classes) оборачивают типы и позволяют получать типобезопасность без лишних выделений памяти в большинстве случаев. Они должны иметь одно свойство в первичном конструкторе, не могут иметь backing fields, init блоки, lateinit/делегаты или наследовать классы, но могут реализовывать интерфейсы. В отличие от псевдонимов типов, которые являются только алиасами, value классы создают отдельные типы. Используйте их для типобезопасных ID, единиц измерения и валидированных оберток.

---

## Answer (EN)

Inline classes (now called **value classes**) are a special kind of class that wraps another type and can be represented as that underlying value at runtime, avoiding separate object allocations in most cases.

### Problem They Solve

Sometimes business logic requires wrapping a type (e.g., IDs, Email, units) to improve type-safety and encapsulate logic, but regular wrappers introduce extra heap allocations and runtime overhead.

```kotlin
// Regular wrapper - creates heap objects
class UserIdBox(val value: String)

val idBox = UserIdBox("12345")  // Heap allocation
```

### Solution: Value Classes

```kotlin
// Value class: in typical usage compiled to operate on String directly
@JvmInline
value class UserId(val value: String)

val id = UserId("12345")
```

Note: in certain usages (nullable, generics, storing as Any, etc.) a value class may be boxed, and an object allocation will occur.

### Syntax

```kotlin
// Modern syntax (Kotlin 1.5+)
@JvmInline
value class Password(val value: String)

// Old syntax (deprecated)
inline class PasswordLegacy(val value: String)
```

### Restrictions

- Must have exactly one property initialized in primary constructor
- Cannot have init blocks
- Properties cannot have backing fields (only computed properties)
- No lateinit or delegated properties
- Cannot extend other classes (must be final)
- Can implement interfaces

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

    init {              // - Init block not allowed
        println("Created")
    }

    lateinit var data: String  // - lateinit not allowed
}
```

### Value Classes Vs Type Aliases

| Feature | Value Class | Type Alias |
|---------|-------------|------------|
| Creates new type | Yes | No (just a name) |
| Type safety | Strong | Weak |
| Runtime overhead | Usually none (except when boxed) | None |
| Can have members | Yes | No |

```kotlin
// Type alias - no type safety
typealias EmailAlias = String
typealias PasswordAlias = String

val email: EmailAlias = "user@example.com"
val password: PasswordAlias = email  // - Compiles! No safety

// Value class - type safety
@JvmInline
value class EmailAddress(val value: String)
@JvmInline
value class PasswordValue(val value: String)

val email2 = EmailAddress("user@example.com")
// val password2: PasswordValue = email2  // - Compilation error! Type safe
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
value class EmailValue private constructor(val value: String) {
    companion object {
        fun create(value: String): EmailValue? {
            return if (value.contains('@')) EmailValue(value) else null
        }
    }
}

// Can only create valid emails
val emailValue = EmailValue.create("user@example.com")  // EmailValue?
val invalidEmail = EmailValue.create("not-an-email")  // null
```

### Performance

Value classes are designed to provide type safety with minimal or zero runtime overhead in typical use cases. When they are used as non-nullable concrete types, the compiler often represents them as the underlying type directly (no wrapper object). When they must be boxed (e.g., nullable value class, used as a generic parameter, stored as Any, etc.), an object is allocated.

```kotlin
@JvmInline
value class Password(val value: String)

fun hashPassword(password: Password): String {
    return password.value.hashCode().toString()
}

// On JVM, this can be compiled equivalently to:
fun hashPassword(value: String): String {
    return value.hashCode().toString()
}
// No Password object needs to be created in this scenario.
```

**English Summary**: Value classes (inline classes) wrap types and can be represented as the underlying value to avoid additional allocations in most cases, while providing strong type safety. They must have a single property in the primary constructor, cannot have backing fields, init blocks, lateinit or delegated properties, and cannot extend other classes, but can implement interfaces. Unlike type aliases (which are just alternative names), value classes create distinct types. They are ideal for type-safe IDs, units of measurement, and validated wrappers. See also [[c-kotlin]].

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid (boxing, nullable usage, generics)?

## References
- [Inline Classes / Value Classes - Kotlin Documentation](https://kotlinlang.org/docs/inline-classes.html)

## Related Questions

### Prerequisites (Easier)
- [[q-inline-value-classes-performance--kotlin--medium]]

### Related (Medium)
- [[q-kotlin-inline-functions--kotlin--medium]]
- [[q-anonymous-class-in-inline-function--kotlin--medium]]

### Advanced (Harder)
- [[q-actor-pattern--kotlin--hard]]

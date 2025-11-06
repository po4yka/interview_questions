---
id: android-069
title: Kotlin Value Classes (Inline Classes) / Value классы в Kotlin
aliases:
- Kotlin Value Classes (Inline Classes)
- Value классы в Kotlin
topic: android
subtopics:
- coroutines
- performance-memory
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
created: 2025-10-12
updated: 2025-10-31
tags:
- android/coroutines
- android/performance-memory
- difficulty/medium
- inline-classes
- performance
- type-safety
- value-classes
sources:
- https://kotlinlang.org/docs/inline-classes.html

---

# Вопрос (RU)
> Что такое value классы в Kotlin и как они работают?

# Question (EN)
> What are value classes in Kotlin and how do they work?

---

## Ответ (RU)

**Теория value классов:**
Value классы (ранее inline классы) предоставляют типобезопасные обёртки вокруг примитивных типов без накладных расходов во время выполнения. Они инлайнятся во время компиляции, обеспечивая типобезопасность без потери производительности.

**Основные особенности:**
- Только одно `val` свойство в первичном конструкторе
- Требуется аннотация `@JvmInline`
- Нулевые накладные расходы при прямом использовании
- Боксинг происходит при использовании как Any, в коллекциях, nullable

**Базовое определение:**
```kotlin
@JvmInline
value class UserId(val value: String)

@JvmInline
value class Email(val value: String)

// Использование - типобезопасность без накладных расходов
fun getUser(userId: UserId): User {
    // Нельзя случайно передать Email
    return userRepository.findById(userId.value)
}

val userId = UserId("user123")
val email = Email("user@example.com")
// getUser(email) // Ошибка компиляции
```

**Сравнение с data классами:**
```kotlin
// Data класс - выделение объекта в куче
data class UserIdData(val value: String)

// Value класс - нет выделения объекта
@JvmInline
value class UserIdValue(val value: String)

// Memory usage:
// Data класс: ~16 байт (заголовок объекта + ссылка)
// Value класс: 0 дополнительных байт
```

**Валидация в value классах:**
```kotlin
@JvmInline
value class Email(val value: String) {
    init {
        require(value.contains("@")) { "Неверный формат email" }
        require(value.length <= 100) { "Email слишком длинный" }
    }

    fun domain(): String = value.substringAfter("@")
}

@JvmInline
value class Quantity(val value: Int) {
    init {
        require(value > 0) { "Количество должно быть положительным" }
    }
}
```

**Распространённые случаи использования:**
```kotlin
// ID и идентификаторы
@JvmInline
value class UserId(val value: String)

@JvmInline
value class OrderId(val value: Long)

// Измерения и единицы
@JvmInline
value class Meters(val value: Double) {
    fun toKilometers(): Kilometers = Kilometers(value / 1000)
}

@JvmInline
value class Kilometers(val value: Double) {
    fun toMeters(): Meters = Meters(value * 1000)
}

// Деньги и валюта
@JvmInline
value class USD(val cents: Long) {
    constructor(dollars: Double) : this((dollars * 100).toLong())

    fun toDollars(): Double = cents / 100.0

    operator fun plus(other: USD): USD = USD(cents + other.cents)
    operator fun minus(other: USD): USD = USD(cents - other.cents)
}
```

**Ограничения и боксинг:**
```kotlin
@JvmInline
value class UserId(val value: String)

// Боксинг происходит в следующих случаях:
val any: Any = userId                    // 1. Использование как Any
val list: List<UserId> = listOf(userId) // 2. В коллекциях
val nullable: UserId? = userId          // 3. Nullable типы
val id: Identifier = userId             // 4. Интерфейсы

// Чтобы избежать боксинга:
// - Используйте value классы напрямую
// - Избегайте nullable когда возможно
// - Рассмотрите обычные классы для коллекций
```

## Answer (EN)

**Value Classes Theory:**
Value classes (formerly inline classes) provide type-safe wrappers around primitive types without runtime overhead. They are inlined at compile time, providing type safety without performance loss.

**Main features:**
- Only one `val` property in primary constructor
- Requires `@JvmInline` annotation
- Zero overhead when used directly
- Boxing occurs when used as Any, in collections, nullable

**Basic definition:**
```kotlin
@JvmInline
value class UserId(val value: String)

@JvmInline
value class Email(val value: String)

// Usage - type safety without runtime overhead
fun getUser(userId: UserId): User {
    // Can't accidentally pass Email
    return userRepository.findById(userId.value)
}

val userId = UserId("user123")
val email = Email("user@example.com")
// getUser(email) // Compile error
```

**Comparison with data classes:**
```kotlin
// Data class - heap object allocation
data class UserIdData(val value: String)

// Value class - no object allocation
@JvmInline
value class UserIdValue(val value: String)

// Memory usage:
// Data class: ~16 bytes (object header + reference)
// Value class: 0 extra bytes
```

**Validation in value classes:**
```kotlin
@JvmInline
value class Email(val value: String) {
    init {
        require(value.contains("@")) { "Invalid email format" }
        require(value.length <= 100) { "Email too long" }
    }

    fun domain(): String = value.substringAfter("@")
}

@JvmInline
value class Quantity(val value: Int) {
    init {
        require(value > 0) { "Quantity must be positive" }
    }
}
```

**Common use cases:**
```kotlin
// IDs and identifiers
@JvmInline
value class UserId(val value: String)

@JvmInline
value class OrderId(val value: Long)

// Measurements and units
@JvmInline
value class Meters(val value: Double) {
    fun toKilometers(): Kilometers = Kilometers(value / 1000)
}

@JvmInline
value class Kilometers(val value: Double) {
    fun toMeters(): Meters = Meters(value * 1000)
}

// Money and currency
@JvmInline
value class USD(val cents: Long) {
    constructor(dollars: Double) : this((dollars * 100).toLong())

    fun toDollars(): Double = cents / 100.0

    operator fun plus(other: USD): USD = USD(cents + other.cents)
    operator fun minus(other: USD): USD = USD(cents - other.cents)
}
```

**Limitations and boxing:**
```kotlin
@JvmInline
value class UserId(val value: String)

// Boxing occurs in these cases:
val any: Any = userId                    // 1. Used as Any
val list: List<UserId> = listOf(userId) // 2. In collections
val nullable: UserId? = userId          // 3. Nullable types
val id: Identifier = userId             // 4. Interfaces

// To avoid boxing:
// - Use value classes directly
// - Avoid nullable when possible
// - Consider regular classes for collections
```

---

## Follow-ups

- What's the difference between value classes and inline classes?
- When should you use value classes vs data classes?
- How do value classes affect binary compatibility?


## References

- [Memory Management](https://developer.android.com/topic/performance/memory-overview)


## Related Questions

### Prerequisites / Concepts

- 


### Prerequisites (Easier)
- [[q-what-is-the-difference-between-measurement-units-like-dp-and-sp--android--easy]] - Unit types basics
- [[q-viewmodel-pattern--android--easy]] - `ViewModel` patterns

### Related (Same Level)
-  - Data classes
- [[q-repository-pattern--android--medium]] - `Repository` pattern
- [[q-parcelable-implementation--android--medium]] - Efficient data passing
- [[q-bundle-data-types--android--medium]] - Data serialization

### Advanced (Harder)
- [[q-kotlin-context-receivers--android--hard]] - `Context` receivers deep dive
- [[q-kotlin-dsl-builders--android--hard]] - DSL builders
- [[q-android-runtime-internals--android--hard]] - Runtime optimization

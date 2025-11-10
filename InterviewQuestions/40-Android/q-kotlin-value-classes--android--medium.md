---
id: kotlin-069
title: Kotlin Value Classes (Inline Classes) / Value классы в Kotlin
aliases:
- Kotlin Value Classes (Inline Classes)
- Value классы в Kotlin
topic: kotlin
subtopics:
- types
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-concepts--kotlin--medium
- q-android-runtime-art--android--medium
created: 2025-10-12
updated: 2025-11-10
tags:
- kotlin/types
- difficulty/medium
- inline-classes
- performance
- type-safety
- value-classes
sources:
- "https://kotlinlang.org/docs/inline-classes.html"

---

# Вопрос (RU)
> Что такое value классы в Kotlin и как они работают?

# Question (EN)
> What are value classes in Kotlin and how do they work?

---

## Ответ (RU)

**Теория value классов:**
Value классы (ранее inline классы) предоставляют типобезопасные обёртки вокруг значений (часто примитивов или простых типов) с минимальными накладными расходами. При прямом использовании они, как правило, представляются как сырое значение без дополнительного объекта, обеспечивая типобезопасность почти без потери производительности. В случаях, когда это невозможно, происходит боксинг.

**Основные особенности:**
- Ровно одно `val` свойство в первичном конструкторе (поддержка `var` отсутствует)
- Требуется аннотация `@JvmInline` для использования на JVM
- При прямом использовании обычно нет дополнительного объекта (репрезентация как значение)
- Боксинг может происходить при использовании как `Any`, в обобщённых контекстах, для nullable-типов и при приведении к интерфейсам

**Базовое определение:**
```kotlin
@JvmInline
value class UserId(val value: String)

@JvmInline
value class Email(val value: String)

// Использование — типобезопасность с минимальными накладными расходами
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
// Data класс — почти всегда создаётся объект в куче
data class UserIdData(val value: String)

// Value класс — при большинстве прямых использований представляется как само значение
@JvmInline
value class UserIdValue(val value: String)

// Память (упрощённо, для JVM):
// Data класс: объект с заголовком + хранение поля
// Value класс: без дополнительного объекта при небоксовом представлении;
// при боксинге создаётся объект-обёртка.
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

val userId = UserId("u1")

// Боксинг может происходить в следующих случаях:
val any: Any = userId                     // 1. Использование как Any
val list: List<UserId> = listOf(userId)   // 2. В обобщениях и коллекциях в определённых ситуациях
val nullable: UserId? = userId            // 3. Nullable типы (обычно боксинг)
// val id: Identifier = userId           // 4. При приведении к интерфейсу (вынуждает боксинг)

// Чтобы уменьшить вероятность боксинга:
// - Используйте value классы напрямую в сигнатурах
// - Избегайте nullable при необходимости максимальной оптимизации
// - Помните, что при некоторых использованиях (Any, интерфейсы, nullable) объект всё же создаётся
```

**Доп. замечание:**
- `value class` — это стабильная эволюция идеи `inline class`: синтаксис и ограничения схожи, но терминология и реализация уточнены; старый синтаксис `inline class` теперь не рекомендуется.

## Answer (EN)

**Value Classes Theory:**
Value classes (formerly inline classes) provide type-safe wrappers around values (often primitives or simple types) with minimal runtime overhead. When used directly, they are typically represented as the underlying value without an extra object, providing type safety with near-zero cost. When this is not possible, boxing is used.

**Main features:**
- Exactly one `val` property in the primary constructor (`var` is not allowed)
- Requires `@JvmInline` annotation on the JVM
- When used directly, usually no additional object allocation (represented as the underlying value)
- Boxing may occur when used as `Any`, in generic contexts, for nullable types, or when converted to interfaces

**Basic definition:**
```kotlin
@JvmInline
value class UserId(val value: String)

@JvmInline
value class Email(val value: String)

// Usage — type safety with minimal overhead
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
// Data class — almost always a heap object allocation
data class UserIdData(val value: String)

// Value class — in most direct usages represented as the raw value
@JvmInline
value class UserIdValue(val value: String)

// Memory usage (simplified, for JVM):
// Data class: full object with header + field storage
// Value class: no separate object when unboxed; when boxed, an object wrapper is allocated.
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

val userId = UserId("u1")

// Boxing may occur in these cases:
val any: Any = userId                     // 1. Used as Any
val list: List<UserId> = listOf(userId)   // 2. In generics/collections in certain cases
val nullable: UserId? = userId            // 3. Nullable types (commonly boxed)
// val id: Identifier = userId           // 4. When treated as an interface type

// To reduce boxing:
// - Use value classes directly in APIs
// - Avoid nullable value-class types when you are optimizing hot paths
// - Be aware that Any/interface/nullable usages will typically allocate a wrapper
```

**Extra note:**
- `value class` is the stabilized evolution of `inline class`; the old `inline class` syntax is deprecated in favor of `value class` with essentially the same conceptual model but refined semantics.

---

## Дополнительные вопросы (RU)

- В чем разница между value классами и inline классами?
- Когда стоит использовать value классы, а когда data классы?
- Как value классы влияют на бинарную совместимость?

## Follow-ups

- What's the difference between value classes and inline classes?
- When should you use value classes vs data classes?
- How do value classes affect binary compatibility?

## Ссылки (RU)

- [Kotlin Value Classes (официальная документация)](https://kotlinlang.org/docs/inline-classes.html)

## References

- [Kotlin Value Classes (official docs)](https://kotlinlang.org/docs/inline-classes.html)

## Related Questions

### Prerequisites / Concepts

- [[c-concepts--kotlin--medium]]


### Prerequisites (Easier)

- [[q-what-is-the-difference-between-measurement-units-like-dp-and-sp--android--easy]] - Unit types basics
- [[q-viewmodel-pattern--android--easy]] - `ViewModel` patterns

### Related (Same Level)

- [[q-android-runtime-art--android--medium]] - Android Runtime (ART)
- [[q-repository-pattern--android--medium]] - Repository pattern
- [[q-parcelable-implementation--android--medium]] - Efficient data passing
- [[q-bundle-data-types--android--medium]] - Data serialization

### Advanced (Harder)

- [[q-kotlin-dsl-builders--android--hard]] - DSL builders
- [[q-android-runtime-internals--android--hard]] - Runtime optimization

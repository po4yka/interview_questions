---
id: "20251012-150017"
title: "Value Classes (Inline Classes) in Kotlin / Value классы в Kotlin"
aliases: ["Value Classes", "Встраиваемые классы"]
topic: kotlin
subtopics: [value-classes, inline-classes, performance]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-data-class-detailed--kotlin--medium, q-inheritance-open-final--kotlin--medium, q-object-singleton-companion--kotlin--medium]
created: "2025-10-12"
updated: 2025-01-25
tags: [kotlin, value-classes, inline-classes, performance, kotlin-features, difficulty/medium]
sources: [https://kotlinlang.org/docs/inline-classes.html]
---

# Вопрос (RU)
> Что такое value классы (inline классы) в Kotlin и зачем они нужны?

# Question (EN)
> What are value classes (inline classes) in Kotlin and why are they needed?

---

## Ответ (RU)

**Теория Value классов:**
Value классы (inline классы) - экспериментальная фича Kotlin, созданная для обёртки одного значения без риска накладных расходов на allocation. Компилятор может встроить класс в базовый тип, избегая упаковки в runtime. Обеспечивает type-safety без overhead - zero-cost abstractions.

**Основные концепции:**
- **Одно property**: Должен иметь ровно один val property
- **Inlining**: Компилятор встраивает класс в базовый тип когда возможно
- **Type safety**: Обеспечивает безопасность типов без накладных расходов
- **No allocation**: Избегает создания wrapper объектов в большинстве случаев

**Базовый синтаксис:**
```kotlin
@JvmInline
value class Password(private val value: String)

@JvmInline
value class UserId(private val id: Long)

// ✅ Использование
val password = Password("secret123")
val userId = UserId(12345L)

// ❌ Нельзя создать без значения
// val badPassword = Password() // Ошибка компиляции
```

**Type safety без allocation:**
```kotlin
@JvmInline
value class Email(private val value: String) {
    init {
        require(value.contains("@")) { "Invalid email" }
    }
}

@JvmInline
value class Username(private val value: String) {
    init {
        require(value.length >= 3) { "Username too short" }
    }
}

// ✅ Различные типы, нет путаницы
fun signup(email: Email, username: Username) {
    println("Email: $email, Username: $username")
}

// ❌ Компилятор не даст перепутать типы
// signup(Username("test"), Email("test@example.com")) // Ошибка!
```

**Требования к value class:**
```kotlin
// ❌ ПЛОХО: больше одного property
// value class Bad(private val a: String, private val b: String)

// ❌ ПЛОХО: var вместо val
// value class Bad(private var value: String)

// ✅ ХОРОШО: ровно один val
@JvmInline
value class Good(private val value: String)

// ✅ ХОРОШО: может иметь methods
@JvmInline
value class Point(val x: Int, val y: Int) {
    fun distance(): Double = Math.sqrt((x * x + y * y).toDouble())
}
```

**Практическое применение:**
```kotlin
@JvmInline
value class Price(val amount: Long) {
    fun format(): String {
        return "$${amount / 100.0}"
    }
}

@JvmInline
value class Minutes(val value: Int) {
    fun toSeconds(): Int = value * 60
}

// ✅ Типобезопасная работа с единицами измерения
fun calculateCost(price: Price, duration: Minutes): String {
    val total = price.amount * duration.value
    return "Total: ${total / 100.0}"
}
```

**Boxing scenarios:**
```kotlin
@JvmInline
value class Id(val value: Int)

// ✅ Inlined: нет boxing
fun processId(id: Id): Int {
    return id.value
}

// ❌ Boxing происходит когда:
interface Wrapper {
    fun getValue(): Id
}

// ❌ Передача в Any
fun boxId(id: Id): Any {
    return id // Boxing здесь
}

// ❌ Использование как nullable
fun nullableId(id: Id?): Id? {
    return id // Boxing здесь
}
```

---

## Answer (EN)

**Value Class Theory:**
Value classes (inline classes) are experimental Kotlin feature for wrapping single value without allocation overhead. Compiler can inline class into underlying type, avoiding wrapping at runtime. Provides type safety without overhead - zero-cost abstractions.

**Core Concepts:**
- **Single property**: Must have exactly one val property
- **Inlining**: Compiler inlines class into underlying type when possible
- **Type safety**: Provides type safety without overhead
- **No allocation**: Avoids creating wrapper objects in most cases

**Basic Syntax:**
```kotlin
@JvmInline
value class Password(private val value: String)

@JvmInline
value class UserId(private val id: Long)

// ✅ Usage
val password = Password("secret123")
val userId = UserId(12345L)

// ❌ Cannot create without value
// val badPassword = Password() // Compilation error
```

**Type Safety Without Allocation:**
```kotlin
@JvmInline
value class Email(private val value: String) {
    init {
        require(value.contains("@")) { "Invalid email" }
    }
}

@JvmInline
value class Username(private val value: String) {
    init {
        require(value.length >= 3) { "Username too short" }
    }
}

// ✅ Different types, no confusion
fun signup(email: Email, username: Username) {
    println("Email: $email, Username: $username")
}

// ❌ Compiler won't let types be confused
// signup(Username("test"), Email("test@example.com")) // Error!
```

**Value Class Requirements:**
```kotlin
// ❌ BAD: more than one property
// value class Bad(private val a: String, private val b: String)

// ❌ BAD: var instead of val
// value class Bad(private var value: String)

// ✅ GOOD: exactly one val
@JvmInline
value class Good(private val value: String)

// ✅ GOOD: can have methods
@JvmInline
value class Point(val x: Int, val y: Int) {
    fun distance(): Double = Math.sqrt((x * x + y * y).toDouble())
}
```

**Practical Application:**
```kotlin
@JvmInline
value class Price(val amount: Long) {
    fun format(): String {
        return "$${amount / 100.0}"
    }
}

@JvmInline
value class Minutes(val value: Int) {
    fun toSeconds(): Int = value * 60
}

// ✅ Type-safe work with measurement units
fun calculateCost(price: Price, duration: Minutes): String {
    val total = price.amount * duration.value
    return "Total: ${total / 100.0}"
}
```

**Boxing Scenarios:**
```kotlin
@JvmInline
value class Id(val value: Int)

// ✅ Inlined: no boxing
fun processId(id: Id): Int {
    return id.value
}

// ❌ Boxing occurs when:
interface Wrapper {
    fun getValue(): Id
}

// ❌ Passing to Any
fun boxId(id: Id): Any {
    return id // Boxing here
}

// ❌ Using as nullable
fun nullableId(id: Id?): Id? {
    return id // Boxing here
}
```

## Follow-ups

- When to use value class vs data class?
- Performance implications of value classes?
- Boxing scenarios to avoid?

## References

- [[c-oop-fundamentals]]
- https://kotlinlang.org/docs/inline-classes.html

## Related Questions

### Prerequisites (Easier)
- [[q-kotlin-enum-classes--kotlin--easy]] - Basic classes

### Related (Medium)
- [[q-data-class-detailed--kotlin--medium]] - Data classes
- [[q-inheritance-open-final--kotlin--medium]] - Inheritance
- [[q-class-initialization-order--kotlin--medium]] - Class initialization

### Advanced (Harder)
- [[q-kotlin-reified-types--kotlin--hard]] - Reified types

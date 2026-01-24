---
id: kotlin-251
title: Design Patterns in Kotlin / Паттерны проектирования в Kotlin
aliases:
- Design Patterns Kotlin
- Kotlin Patterns
- Паттерны проектирования Kotlin
topic: kotlin
subtopics:
- design-patterns
- oop
- functional
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- c-design-patterns
created: 2026-01-23
updated: 2026-01-23
tags:
- kotlin
- design-patterns
- builder
- strategy
- factory
- difficulty/medium
anki_cards:
- slug: kotlin-251-0-en
  language: en
  anki_id: 1769170293571
  synced_at: '2026-01-23T17:03:50.433450'
- slug: kotlin-251-0-ru
  language: ru
  anki_id: 1769170293595
  synced_at: '2026-01-23T17:03:50.436473'
---
# Вопрос (RU)
> Как реализуются классические паттерны проектирования в Kotlin? Приведи примеры Builder, Strategy и Factory.

# Question (EN)
> How are classic design patterns implemented in Kotlin? Give examples of Builder, Strategy, and Factory.

---

## Ответ (RU)

Kotlin предлагает идиоматичные способы реализации паттернов благодаря языковым возможностям.

**Builder Pattern - через DSL:**
```kotlin
// Вместо классического Builder используем DSL
class Email private constructor(
    val to: String,
    val subject: String,
    val body: String
) {
    class Builder {
        var to: String = ""
        var subject: String = ""
        var body: String = ""

        fun build() = Email(to, subject, body)
    }
}

// DSL функция
fun email(block: Email.Builder.() -> Unit): Email {
    return Email.Builder().apply(block).build()
}

// Использование
val mail = email {
    to = "user@example.com"
    subject = "Hello"
    body = "Kotlin DSL is great!"
}
```

**Strategy Pattern - через лямбды:**
```kotlin
// Вместо интерфейса с классами используем функции
class PaymentProcessor(
    private val strategy: (amount: Double) -> Boolean
) {
    fun process(amount: Double) = strategy(amount)
}

// Стратегии как лямбды
val creditCard: (Double) -> Boolean = { amount ->
    println("Paying $amount via credit card")
    true
}

val paypal: (Double) -> Boolean = { amount ->
    println("Paying $amount via PayPal")
    true
}

// Использование
val processor = PaymentProcessor(creditCard)
processor.process(100.0)
```

**Factory Pattern - через companion object:**
```kotlin
sealed class Notification {
    data class Email(val address: String) : Notification()
    data class SMS(val phone: String) : Notification()
    data class Push(val token: String) : Notification()

    companion object {
        fun create(type: String, target: String): Notification = when (type) {
            "email" -> Email(target)
            "sms" -> SMS(target)
            "push" -> Push(target)
            else -> throw IllegalArgumentException("Unknown type")
        }
    }
}

// Использование
val notification = Notification.create("email", "user@example.com")
```

**Singleton - через object:**
```kotlin
object DatabaseConnection {
    init { println("Initializing connection") }
    fun query(sql: String) { /* ... */ }
}
```

**Decorator - через delegation:**
```kotlin
interface Coffee { fun cost(): Double }

class SimpleCoffee : Coffee {
    override fun cost() = 1.0
}

class MilkDecorator(private val coffee: Coffee) : Coffee by coffee {
    override fun cost() = coffee.cost() + 0.5
}
```

## Answer (EN)

Kotlin offers idiomatic ways to implement patterns thanks to language features.

**Builder Pattern - via DSL:**
```kotlin
// Instead of classic Builder, use DSL
class Email private constructor(
    val to: String,
    val subject: String,
    val body: String
) {
    class Builder {
        var to: String = ""
        var subject: String = ""
        var body: String = ""

        fun build() = Email(to, subject, body)
    }
}

// DSL function
fun email(block: Email.Builder.() -> Unit): Email {
    return Email.Builder().apply(block).build()
}

// Usage
val mail = email {
    to = "user@example.com"
    subject = "Hello"
    body = "Kotlin DSL is great!"
}
```

**Strategy Pattern - via lambdas:**
```kotlin
// Instead of interface with classes, use functions
class PaymentProcessor(
    private val strategy: (amount: Double) -> Boolean
) {
    fun process(amount: Double) = strategy(amount)
}

// Strategies as lambdas
val creditCard: (Double) -> Boolean = { amount ->
    println("Paying $amount via credit card")
    true
}

val paypal: (Double) -> Boolean = { amount ->
    println("Paying $amount via PayPal")
    true
}

// Usage
val processor = PaymentProcessor(creditCard)
processor.process(100.0)
```

**Factory Pattern - via companion object:**
```kotlin
sealed class Notification {
    data class Email(val address: String) : Notification()
    data class SMS(val phone: String) : Notification()
    data class Push(val token: String) : Notification()

    companion object {
        fun create(type: String, target: String): Notification = when (type) {
            "email" -> Email(target)
            "sms" -> SMS(target)
            "push" -> Push(target)
            else -> throw IllegalArgumentException("Unknown type")
        }
    }
}

// Usage
val notification = Notification.create("email", "user@example.com")
```

**Singleton - via object:**
```kotlin
object DatabaseConnection {
    init { println("Initializing connection") }
    fun query(sql: String) { /* ... */ }
}
```

**Decorator - via delegation:**
```kotlin
interface Coffee { fun cost(): Double }

class SimpleCoffee : Coffee {
    override fun cost() = 1.0
}

class MilkDecorator(private val coffee: Coffee) : Coffee by coffee {
    override fun cost() = coffee.cost() + 0.5
}
```

---

## Follow-ups

- How does Kotlin's `by` delegation simplify the Decorator pattern?
- What is the @DslMarker annotation used for?
- How would you implement the Observer pattern using Flow?

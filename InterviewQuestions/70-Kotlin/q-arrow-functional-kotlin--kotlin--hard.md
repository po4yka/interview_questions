---
id: kotlin-253
title: Arrow and Functional Kotlin / Arrow и функциональный Kotlin
aliases:
- Arrow Library
- Functional Programming Kotlin
- Arrow и функциональный Kotlin
topic: kotlin
subtopics:
- functional
- arrow
- error-handling
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- c-functional
created: 2026-01-23
updated: 2026-01-23
tags:
- kotlin
- arrow
- functional
- either
- monad
- difficulty/hard
anki_cards:
- slug: kotlin-253-0-en
  language: en
  anki_id: 1769170361996
  synced_at: '2026-01-23T17:03:51.705847'
- slug: kotlin-253-0-ru
  language: ru
  anki_id: 1769170362021
  synced_at: '2026-01-23T17:03:51.706899'
---
# Вопрос (RU)
> Что такое Arrow в Kotlin? Как использовать Either и другие функциональные типы для обработки ошибок?

# Question (EN)
> What is Arrow in Kotlin? How do you use Either and other functional types for error handling?

---

## Ответ (RU)

**Arrow** - библиотека функционального программирования для Kotlin, предоставляющая типы и паттерны из FP.

**Ключевые типы:**

| Тип | Описание | Использование |
|-----|----------|---------------|
| `Either<E, A>` | Результат или ошибка | Обработка ошибок без исключений |
| `Option<A>` | Значение или отсутствие | Замена nullable |
| `Validated<E, A>` | Накопление ошибок | Валидация форм |

**Either - обработка ошибок:**
```kotlin
import arrow.core.*

sealed class AppError {
    data class NetworkError(val message: String) : AppError()
    data class ValidationError(val field: String) : AppError()
}

// Функция возвращает Either
fun fetchUser(id: String): Either<AppError, User> {
    return if (id.isBlank()) {
        AppError.ValidationError("id").left()
    } else {
        User(id, "John").right()
    }
}

// Использование
val result = fetchUser("123")
    .map { user -> user.name }
    .mapLeft { error -> "Error: $error" }

when (result) {
    is Either.Left -> println(result.value)
    is Either.Right -> println(result.value)
}
```

**Raise DSL (Arrow 2.0):**
```kotlin
import arrow.core.raise.*

fun Raise<AppError>.processUser(id: String): User {
    ensure(id.isNotBlank()) { AppError.ValidationError("id") }
    val user = fetchUserOrNull(id) ?: raise(AppError.NetworkError("Not found"))
    return user
}

// Запуск
val result: Either<AppError, User> = either {
    processUser("123")
}
```

**Validated - накопление ошибок:**
```kotlin
import arrow.core.*

data class FormData(val email: String, val age: Int)

fun validateEmail(email: String): ValidatedNel<String, String> =
    if (email.contains("@")) email.validNel()
    else "Invalid email".invalidNel()

fun validateAge(age: Int): ValidatedNel<String, Int> =
    if (age >= 18) age.validNel()
    else "Must be 18+".invalidNel()

// Комбинирование валидаций
fun validateForm(email: String, age: Int): ValidatedNel<String, FormData> =
    validateEmail(email).zip(validateAge(age)) { e, a -> FormData(e, a) }

// Результат содержит ВСЕ ошибки, а не первую
val result = validateForm("invalid", 15)
// Invalid(NonEmptyList(Invalid email, Must be 18+))
```

**Option вместо null:**
```kotlin
import arrow.core.*

fun findUser(id: String): Option<User> =
    users[id]?.some() ?: none()

val name = findUser("123")
    .map { it.name }
    .getOrElse { "Unknown" }
```

## Answer (EN)

**Arrow** - functional programming library for Kotlin, providing FP types and patterns.

**Key Types:**

| Type | Description | Use Case |
|------|-------------|----------|
| `Either<E, A>` | Result or error | Error handling without exceptions |
| `Option<A>` | Value or absence | Replacing nullable |
| `Validated<E, A>` | Error accumulation | Form validation |

**Either - Error Handling:**
```kotlin
import arrow.core.*

sealed class AppError {
    data class NetworkError(val message: String) : AppError()
    data class ValidationError(val field: String) : AppError()
}

// Function returns Either
fun fetchUser(id: String): Either<AppError, User> {
    return if (id.isBlank()) {
        AppError.ValidationError("id").left()
    } else {
        User(id, "John").right()
    }
}

// Usage
val result = fetchUser("123")
    .map { user -> user.name }
    .mapLeft { error -> "Error: $error" }

when (result) {
    is Either.Left -> println(result.value)
    is Either.Right -> println(result.value)
}
```

**Raise DSL (Arrow 2.0):**
```kotlin
import arrow.core.raise.*

fun Raise<AppError>.processUser(id: String): User {
    ensure(id.isNotBlank()) { AppError.ValidationError("id") }
    val user = fetchUserOrNull(id) ?: raise(AppError.NetworkError("Not found"))
    return user
}

// Running
val result: Either<AppError, User> = either {
    processUser("123")
}
```

**Validated - Error Accumulation:**
```kotlin
import arrow.core.*

data class FormData(val email: String, val age: Int)

fun validateEmail(email: String): ValidatedNel<String, String> =
    if (email.contains("@")) email.validNel()
    else "Invalid email".invalidNel()

fun validateAge(age: Int): ValidatedNel<String, Int> =
    if (age >= 18) age.validNel()
    else "Must be 18+".invalidNel()

// Combining validations
fun validateForm(email: String, age: Int): ValidatedNel<String, FormData> =
    validateEmail(email).zip(validateAge(age)) { e, a -> FormData(e, a) }

// Result contains ALL errors, not just first
val result = validateForm("invalid", 15)
// Invalid(NonEmptyList(Invalid email, Must be 18+))
```

**Option instead of null:**
```kotlin
import arrow.core.*

fun findUser(id: String): Option<User> =
    users[id]?.some() ?: none()

val name = findUser("123")
    .map { it.name }
    .getOrElse { "Unknown" }
```

---

## Follow-ups

- What is the difference between Either and Validated?
- How does Arrow's Raise DSL compare to traditional try-catch?
- When should you use Arrow vs Kotlin's Result type?

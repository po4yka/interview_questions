---
id: cs-033
title: "Nothing Class Purpose / Назначение класса Nothing"
aliases: ["Nothing Class", "Класс Nothing"]
topic: cs
subtopics: [control-flow, exceptions, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [q-sealed-classes-vs-enum--programming-languages--medium, q-smart-casts-how--programming-languages--easy, q-unit-type-purpose--programming-languages--medium]
created: 2025-10-15
updated: 2025-01-25
tags: [control-flow, difficulty/medium, exceptions, kotlin, type-system, unreachable-code]
sources: [https://kotlinlang.org/docs/whatsnew15.html]
---

# Вопрос (RU)
> Зачем нужен класс Nothing в Kotlin? Какую роль он играет в системе типов?

# Question (EN)
> Why is the Nothing class needed in Kotlin? What role does it play in the type system?

---

## Ответ (RU)

**Теория Nothing Type:**
Nothing - type that has no values, represents unreachable code и denotes operations that never complete normally. Nothing - bottom type в Kotlin hierarchy, является subtype всех types. Используется для: static analysis, smart casts, code optimization, unreachable code detection.

**Определение:**

*Теория:* Nothing - special type representing no possible value. Обозначает функции, которые never return normally - either throw exception или run infinitely. Компилятор использует Nothing для inferring unreachable code paths. Nothing - bottom type - subtype всего, что позволяет ему быть "safe" в любом context.

```kotlin
// ✅ Nothing для functions что never return
fun fail(message: String): Nothing {
    throw IllegalArgumentException(message)
}

// ✅ Компилятор знает: код после error недостижим
fun processValue(value: String?): String {
    val result = value ?: error("Value cannot be null")
    // value здесь non-null (smart cast)
    return result.uppercase()
}

// ✅ Infinite loop - never returns
fun eventLoop(): Nothing {
    while (true) {
        handleEvent(waitForEvent())
    }
}
```

**Ключевое использование:**

**1. Static Code Analysis:**
*Теория:* Compiler использует Nothing для control flow analysis. Если function возвращает Nothing, compiler знает что code after call недостижим. Это enables: smart casts (value becomes non-null), unreachable code detection, code optimization. Помогает prevent errors и improves performance.

```kotlin
// ✅ Smart cast после Nothing
fun validateString(value: String?): String {
    if (value == null) {
        throw IllegalArgumentException("Null value")  // Returns Nothing
    }
    // value здесь smart cast к String
    return value.uppercase()  // No null check needed
}

// ✅ Compiler знает: division safe
fun divide(a: Int, b: Int): Int {
    if (b == 0) {
        throw IllegalArgumentException("Cannot divide by zero")  // Nothing
    }
    // Compiler knows b != 0
    return a / b  // Safe division
}
```

**2. Error Functions:**
*Теория:* error() и TODO() возвращают Nothing, потому что они always throw exceptions. Это позволяет compiler infer что code после них unreachable. Улучшает code safety и static analysis.

```kotlin
// ✅ Standard library error() возвращает Nothing
fun require(condition: Boolean, message: () -> String) {
    if (!condition) {
        error(message())  // Never returns
    }
}

// ✅ Usage: smart cast после require
fun processUser(user: User?) {
    require(user != null) { "User cannot be null" }
    // user здесь non-null
    println(user.name)  // No null check needed
}

// ✅ TODO() тоже возвращает Nothing
fun calculateTax(amount: Double): Double {
    TODO("Not implemented yet")
    // Code here недостижим
}

// ✅ Custom error handler
fun requireNonNull(value: String?): String {
    return value ?: throw IllegalArgumentException("Value is null")
}
```

**3. Type Hierarchy (Bottom Type):**
*Теория:* Nothing - bottom type в Kotlin. Это значит что Nothing является subtype всех types. Это позволяет Nothing be used в любом type context. Поддерживает type safety и allows creating generic functions что "never return but can return any type".

```kotlin
// ✅ Nothing - subtype всего
val stringOrNothing: String = TODO()  // Valid: Nothing → String
val intOrNothing: Int = error("Error")  // Valid: Nothing → Int
val anyTypeOrNothing: Any = TODO()  // Valid: Nothing → Any

// ✅ Generic function using Nothing
fun <T> fail(): T = throw Exception()

val str: String = fail()  // T inferred as String, Nothing → String
val num: Int = fail()     // T inferred as Int, Nothing → Int

// ✅ Type hierarchy
// Any (top type)
//   ↓
// All concrete types
//   ↓
// Nothing (bottom type - subtype of all)
```

**4. Nullable Nothing:**
*Теория:* `Nothing?` - type который может быть только null. Useful для empty collections, nullable lists, functions что always return null. Represent "no value" в type-safe way.

```kotlin
// ✅ Nothing? может быть только null
val onlyNull: Nothing? = null  // Only valid value

// ✅ Empty collections
val emptyList: List<Nothing> = emptyList()
// emptyList не может содержать elements (Nothing has no values)

// ✅ Functions always returning null
fun alwaysNull(): Nothing? = null
fun validateAndReturnNull(): Nothing? {
    if (someCondition) {
        throw Exception()  // Returns Nothing, not Nothing?
    }
    return null  // Returns Nothing?
}
```

**Компоненты Nothing:**

**1. Unreachable Code Detection:**
*Теория:* Compiler analyzes code paths. Если code после function call unreachable (function returns Nothing), compiler может: warn о unreachable code, optimize code (remove unreachable branches), improve smart casts (know that variable cannot be null).

```kotlin
// ✅ Unreachable code warning
fun process() {
    if (someCondition) {
        return
    }
    error("Should not happen")  // Returns Nothing
    println("Unreachable")  // Compiler warning
}

// ✅ Exhaustive when
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
}

fun <T> handleResult(result: Result<T>): T {
    return when (result) {
        is Result.Success -> result.data  // T
        is Result.Error -> error(result.message)  // Nothing → T
    }
}
```

**2. Smart Casts:**
*Теория:* Smart casting - automatic type casting based на control flow. Nothing улучшает smart casting: если function returns Nothing после null check, compiler knows variable cannot be null after check. Eliminates need для !! operator или ?. null checks.

```kotlin
// ✅ Smart cast после Nothing
fun safeCast(obj: Any): String {
    return obj as? String ?: error("Not a string")
    // obj as? String → String?
    // error() → Nothing
    // String? ?: Nothing → String
}

// ✅ Null checks with Nothing
fun processNonNull(value: String?): Int {
    val nonNull = value ?: throw IllegalArgumentException("Value is null")
    // Smart cast: nonNull теперь String
    return nonNull.length
}

// ✅ Using require for smart casts
fun <T> List<T>.getOrThrow(index: Int): T {
    require(index in indices) { "Index out of bounds" }
    return this[index]  // No bounds check needed
}
```

**Практические примеры:**

**1. Validation Helpers:**
*Теория:* require(), check(), assert() используют Nothing для создания validation helpers. После call value becomes non-null или condition становится true в view of compiler. Это enables type-safe validation без manual null checks.

```kotlin
// ✅ Preconditions с Nothing
fun divide(a: Int, b: Int): Int {
    require(b != 0) { "Divisor cannot be zero" }
    // Compiler knows b != 0
    return a / b
}

// ✅ Check condition
fun processUser(user: User?) {
    check(user != null) { "User must not be null" }
    // user smart cast to non-null
    println(user.name)
}

// ✅ Assert в debug
fun calculate(value: Int): Int {
    val result = value * 2
    assert(result >= 0) { "Result should be positive" }
    return result
}
```

**2. Early Returns:**
*Теория:* Using Nothing для early returns в validation. Если validation fails, throw exception (returns Nothing), остальной code недостижим. This enables safe access без null checks в rest of function.

```kotlin
// ✅ Early return с exception
fun findUser(id: Int): User {
    val user = database.findById(id) ?: throw NotFoundException("User not found")
    // user guaranteed non-null after this
    return user
}

// ✅ Precondition checks
fun processConfig(config: Config) {
    require(config.isValid()) { "Invalid configuration" }
    // config guaranteed valid
    initializeWith(config)
}
```

**Nothing vs Unit vs Void:**

*Теория:* Unit - функция completed successfully но не возвращает useful value. Nothing - функция never completes normally. Void (Java) - similar to Unit. Nothing unique в том что он represents unreachable code и bottom type.

```kotlin
// ✅ Unit - returns successfully, no value
fun printMessage(msg: String): Unit {
    println(msg)
    // Returns normally
}

// ✅ Nothing - never returns
fun failWithMessage(msg: String): Nothing {
    throw Exception(msg)
    // Never returns
}

// Comparison:
// Unit: Function completes but has no return value
// Nothing: Function never completes
// Void (Java): Similar to Unit
```

## Answer (EN)

**Nothing Type Theory:**
Nothing - type that has no values, represents unreachable code and denotes operations that never complete normally. Nothing - bottom type in Kotlin hierarchy, is subtype of all types. Used for: static analysis, smart casts, code optimization, unreachable code detection.

**Definition:**

*Theory:* Nothing - special type representing no possible value. Denotes functions that never return normally - either throw exception or run infinitely. Compiler uses Nothing for inferring unreachable code paths. Nothing - bottom type - subtype of everything, which allows it to be "safe" in any context.

```kotlin
// ✅ Nothing for functions that never return
fun fail(message: String): Nothing {
    throw IllegalArgumentException(message)
}

// ✅ Compiler knows: code after error is unreachable
fun processValue(value: String?): String {
    val result = value ?: error("Value cannot be null")
    // value here is non-null (smart cast)
    return result.uppercase()
}

// ✅ Infinite loop - never returns
fun eventLoop(): Nothing {
    while (true) {
        handleEvent(waitForEvent())
    }
}
```

**Key Uses:**

**1. Static Code Analysis:**
*Theory:* Compiler uses Nothing for control flow analysis. If function returns Nothing, compiler knows that code after call is unreachable. This enables: smart casts (value becomes non-null), unreachable code detection, code optimization. Helps prevent errors and improves performance.

```kotlin
// ✅ Smart cast after Nothing
fun validateString(value: String?): String {
    if (value == null) {
        throw IllegalArgumentException("Null value")  // Returns Nothing
    }
    // value here smart cast to String
    return value.uppercase()  // No null check needed
}

// ✅ Compiler knows: division safe
fun divide(a: Int, b: Int): Int {
    if (b == 0) {
        throw IllegalArgumentException("Cannot divide by zero")  // Nothing
    }
    // Compiler knows b != 0
    return a / b  // Safe division
}
```

**2. Error Functions:**
*Theory:* error() and TODO() return Nothing because they always throw exceptions. This allows compiler to infer that code after them is unreachable. Improves code safety and static analysis.

```kotlin
// ✅ Standard library error() returns Nothing
fun require(condition: Boolean, message: () -> String) {
    if (!condition) {
        error(message())  // Never returns
    }
}

// ✅ Usage: smart cast after require
fun processUser(user: User?) {
    require(user != null) { "User cannot be null" }
    // user here is non-null
    println(user.name)  // No null check needed
}

// ✅ TODO() also returns Nothing
fun calculateTax(amount: Double): Double {
    TODO("Not implemented yet")
    // Code here is unreachable
}

// ✅ Custom error handler
fun requireNonNull(value: String?): String {
    return value ?: throw IllegalArgumentException("Value is null")
}
```

**3. Type Hierarchy (Bottom Type):**
*Theory:* Nothing - bottom type in Kotlin. This means Nothing is subtype of all types. This allows Nothing to be used in any type context. Supports type safety and allows creating generic functions that "never return but can return any type".

```kotlin
// ✅ Nothing - subtype of everything
val stringOrNothing: String = TODO()  // Valid: Nothing → String
val intOrNothing: Int = error("Error")  // Valid: Nothing → Int
val anyTypeOrNothing: Any = TODO()  // Valid: Nothing → Any

// ✅ Generic function using Nothing
fun <T> fail(): T = throw Exception()

val str: String = fail()  // T inferred as String, Nothing → String
val num: Int = fail()     // T inferred as Int, Nothing → Int

// ✅ Type hierarchy
// Any (top type)
//   ↓
// All concrete types
//   ↓
// Nothing (bottom type - subtype of all)
```

**4. Nullable Nothing:**
*Theory:* `Nothing?` - type that can only be null. Useful for empty collections, nullable lists, functions that always return null. Represent "no value" in type-safe way.

```kotlin
// ✅ Nothing? can only be null
val onlyNull: Nothing? = null  // Only valid value

// ✅ Empty collections
val emptyList: List<Nothing> = emptyList()
// emptyList cannot contain elements (Nothing has no values)

// ✅ Functions always returning null
fun alwaysNull(): Nothing? = null
fun validateAndReturnNull(): Nothing? {
    if (someCondition) {
        throw Exception()  // Returns Nothing, not Nothing?
    }
    return null  // Returns Nothing?
}
```

**Nothing Components:**

**1. Unreachable Code Detection:**
*Theory:* Compiler analyzes code paths. If code after function call is unreachable (function returns Nothing), compiler can: warn about unreachable code, optimize code (remove unreachable branches), improve smart casts (know that variable cannot be null).

```kotlin
// ✅ Unreachable code warning
fun process() {
    if (someCondition) {
        return
    }
    error("Should not happen")  // Returns Nothing
    println("Unreachable")  // Compiler warning
}

// ✅ Exhaustive when
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
}

fun <T> handleResult(result: Result<T>): T {
    return when (result) {
        is Result.Success -> result.data  // T
        is Result.Error -> error(result.message)  // Nothing → T
    }
}
```

**2. Smart Casts:**
*Theory:* Smart casting - automatic type casting based on control flow. Nothing improves smart casting: if function returns Nothing after null check, compiler knows variable cannot be null after check. Eliminates need for !! operator or ?. null checks.

```kotlin
// ✅ Smart cast after Nothing
fun safeCast(obj: Any): String {
    return obj as? String ?: error("Not a string")
    // obj as? String → String?
    // error() → Nothing
    // String? ?: Nothing → String
}

// ✅ Null checks with Nothing
fun processNonNull(value: String?): Int {
    val nonNull = value ?: throw IllegalArgumentException("Value is null")
    // Smart cast: nonNull now String
    return nonNull.length
}

// ✅ Using require for smart casts
fun <T> List<T>.getOrThrow(index: Int): T {
    require(index in indices) { "Index out of bounds" }
    return this[index]  // No bounds check needed
}
```

**Practical Examples:**

**1. Validation Helpers:**
*Theory:* require(), check(), assert() use Nothing to create validation helpers. After call value becomes non-null or condition becomes true in view of compiler. This enables type-safe validation without manual null checks.

```kotlin
// ✅ Preconditions with Nothing
fun divide(a: Int, b: Int): Int {
    require(b != 0) { "Divisor cannot be zero" }
    // Compiler knows b != 0
    return a / b
}

// ✅ Check condition
fun processUser(user: User?) {
    check(user != null) { "User must not be null" }
    // user smart cast to non-null
    println(user.name)
}

// ✅ Assert in debug
fun calculate(value: Int): Int {
    val result = value * 2
    assert(result >= 0) { "Result should be positive" }
    return result
}
```

**2. Early Returns:**
*Theory:* Using Nothing for early returns in validation. If validation fails, throw exception (returns Nothing), rest of code is unreachable. This enables safe access without null checks in rest of function.

```kotlin
// ✅ Early return with exception
fun findUser(id: Int): User {
    val user = database.findById(id) ?: throw NotFoundException("User not found")
    // user guaranteed non-null after this
    return user
}

// ✅ Precondition checks
fun processConfig(config: Config) {
    require(config.isValid()) { "Invalid configuration" }
    // config guaranteed valid
    initializeWith(config)
}
```

**Nothing vs Unit vs Void:**

*Theory:* Unit - function completed successfully but doesn't return useful value. Nothing - function never completes normally. Void (Java) - similar to Unit. Nothing unique in that it represents unreachable code and bottom type.

```kotlin
// ✅ Unit - returns successfully, no value
fun printMessage(msg: String): Unit {
    println(msg)
    // Returns normally
}

// ✅ Nothing - never returns
fun failWithMessage(msg: String): Nothing {
    throw Exception(msg)
    // Never returns
}

// Comparison:
// Unit: Function completes but has no return value
// Nothing: Function never completes
// Void (Java): Similar to Unit
```

---

## Follow-ups

- What is the difference between Nothing and Unit?
- How does Nothing enable smart casts in Kotlin?
- When should you use `Nothing?` instead of `Nothing`?

## Related Questions

### Prerequisites (Easier)
- Basic Kotlin type system concepts
- Null safety and smart casts

### Related (Same Level)
- [[q-unit-type-purpose--programming-languages--medium]] - Unit type
- [[q-smart-casts-how--programming-languages--easy]] - Smart casts
- [[q-sealed-classes-vs-enum--programming-languages--medium]] - Sealed classes

### Advanced (Harder)
- Advanced type system concepts
- Generic programming with Nothing
- Type-safe error handling patterns

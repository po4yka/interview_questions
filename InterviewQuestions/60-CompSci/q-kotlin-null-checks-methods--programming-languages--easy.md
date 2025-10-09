---
tags:
  - elvis
  - kotlin
  - null-checks
  - null-safety
  - operators
  - programming-languages
  - safe-call
difficulty: easy
status: reviewed
---

# Каким образом осуществлять проверки на null?

**English**: How to perform null checks?

## Answer

Kotlin offers several operators and methods for null checking:

### 1. Safe Call Operator `?.`

Returns null if object is null, otherwise calls the method/property:

```kotlin
val length: Int? = name?.length  // Returns null if name is null

val upper: String? = text?.uppercase()?.trim()  // Chain safe calls
```

### 2. Elvis Operator `?:`

Provides default value if expression is null:

```kotlin
val length = name?.length ?: 0  // Returns 0 if name is null

val text = nullableText ?: "default"

// Can throw exception as default
val nonNull = value ?: throw IllegalArgumentException("Value required")
```

### 3. Explicit Check with `if`

Traditional null check:

```kotlin
if (name != null) {
    // Smart cast: name is String here, not String?
    println(name.length)
}

val length = if (name != null) name.length else 0
```

### 4. `requireNotNull()`

Throws exception if null:

```kotlin
val nonNull: String = requireNotNull(nullable) {
    "Value cannot be null"
}

requireNotNull(user) // Throws IllegalArgumentException if null
```

### 5. Double Bang `!!` Operator

Guarantees not-null, throws NPE if null:

```kotlin
val length: Int = name!!.length  // NPE if name is null

// Use sparingly, only when 100% sure value is not null
```

### 6. `let` with Safe Call

Execute block only if not null:

```kotlin
name?.let {
    // 'it' is non-null String here
    println("Name is: $it")
}

// With custom parameter name
user?.let { u ->
    println("User: ${u.name}")
}
```

### 7. `takeIf` / `takeUnless`

Conditional return:

```kotlin
val positiveNumber = number.takeIf { it > 0 }  // null if <= 0

val validEmail = email.takeIf { it.contains("@") }
```

**Best practices:**
- Prefer safe call `?.` and Elvis `?:` over `!!`
- Use `!!` only when you're absolutely certain value is not null
- Use `requireNotNull()` for precondition checks
- Combine operators for concise null handling

## Ответ

Kotlin предлагает операторы безопасного вызова (?.), оператор Элвиса (?:), явную проверку через if (x != null), requireNotNull или !! — для гарантии не-null.


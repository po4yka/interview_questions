---
tags:
  - double-bang
  - kotlin
  - not-null-assertion
  - null-safety
  - operators
  - programming-languages
difficulty: medium
---

# Что известно о double bang (!!)?

**English**: What do you know about double bang (!!)?

## Answer

The `!!` operator (not-null assertion) is used to **explicitly indicate that a value is not null**.

**Behavior:**
- If value is **not null**: Returns the value
- If value **is null**: Throws `KotlinNullPointerException`

**Example:**
```kotlin
var nullable: String? = "Hello"
val length = nullable!!.length  // OK, returns 5

nullable = null
val length2 = nullable!!.length  // Throws KotlinNullPointerException!
```

**When it's used:**

```kotlin
// When you're absolutely sure value is not null
fun process(input: String?) {
    val trimmed = input!!.trim()  // "I know it's not null!"
}

// Better alternatives:
fun process(input: String?) {
    // Option 1: Safe call
    val trimmed = input?.trim()

    // Option 2: Elvis operator
    val trimmed = input?.trim() ?: return

    // Option 3: let
    input?.let { trimmed ->
        // Use trimmed
    }
}
```

**Why it's generally discouraged:**

1. **Defeats null safety**: One of Kotlin's main features
2. **Hard to debug**: Stack trace shows `!!` location, not actual cause
3. **Crashes app**: Just like Java's NullPointerException
4. **Better alternatives exist**: Safe calls, Elvis operator, let

**Legitimate use cases:**

- Interfacing with legacy Java code
- After explicit null check (but smart casts are better)
- Platform types from Java (but better to use safe calls)

**Best practice:** Avoid `!!` and use safer alternatives like `?.`, `?:`, or proper null checks.

## Ответ

Оператор !! используется для явного указания, что значение не null. При использовании !! если значение оказывается null выбрасывается исключение KotlinNullPointerException. Рекомендуется избегать !! и использовать безопасные вызовы (?.) или оператор ?: для обработки null.


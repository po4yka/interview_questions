---
tags:
  - const
  - constants
  - fundamentals
  - immutability
  - kotlin
  - programming-languages
  - val
difficulty: easy
---

# Что такое константы и можно ли их изменять?

**English**: What are constants and can they be changed?

## Answer

Constants are fixed values that cannot be changed after their definition. They are used to define values that remain unchanged throughout program execution.

**In Kotlin:**

- **`val`**: Immutable variable (read-only), value assigned once at runtime
```kotlin
val name = "John" // Cannot reassign
```

- **`const val`**: Compile-time constant (must be top-level or in object, primitive or String)
```kotlin
const val MAX_SIZE = 100 // Known at compile time
```

**Key differences:**
- `val` can be initialized at runtime
- `const val` must be known at compile time
- `const val` can only be used with primitive types and String

Constants are **immutable** - their value cannot be changed after definition.

## Ответ

Константы — это фиксированные значения, которые не могут быть изменены после их определения...


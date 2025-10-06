---
tags:
  - kotlin
  - oop
  - programming-languages
  - sealed-classes
  - type-hierarchy
  - when-expressions
difficulty: medium
---

# Что такое sealed классы и зачем они нужны?

**English**: What are sealed classes and why are they needed?

## Answer

Sealed classes in Kotlin allow **restricting the set of subclasses** that can be created for a class, providing a strict, closed hierarchy.

**Why they're needed:**

1. **Finite set of states**: Perfect for data that can have a limited number of states
```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}
```

2. **Exhaustive when expressions**: Compiler checks all cases are covered
```kotlin
when (result) {
    is Result.Success -> showData(result.data)
    is Result.Error -> showError(result.message)
    Result.Loading -> showLoading()
    // No 'else' needed - compiler knows all cases!
}
```

3. **Type safety**: All possible types known at compile time

4. **Better than enums**: Can have different properties and methods per subclass

**Benefits:**
- Code is more safe and understandable
- Compiler helps catch missing cases
- Better than using multiple nullable fields
- Perfect for state machines, API responses, navigation

## Ответ

Sealed классы в Kotlin позволяют ограничить набор подклассов, которые могут быть созданы для этого класса, обеспечивая строгую иерархию...


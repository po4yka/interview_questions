---
topic: kotlin
id: "20251012-150012"
title: "Sealed classes vs sealed interfaces in Kotlin"
description: "Comprehensive guide to sealed classes and sealed interfaces covering exhaustive when expressions, hierarchy, comparison with enums, and Kotlin 1.5+ features"
tags: ["kotlin", "classes", "sealed", "polymorphism", "when-expression", "difficulty/medium"]
topic: "kotlin"
subtopics: ["classes", "sealed", "polymorphism", "when-expression"]
moc: "moc-kotlin"
status: "draft"
date_created: "2025-10-12"
date_updated: "2025-10-12"
---

# Sealed classes vs sealed interfaces in Kotlin

## English

### Problem Statement

Sealed classes and sealed interfaces restrict class hierarchies, enabling exhaustive when expressions. What are their differences, use cases, and how do they compare to enums?

### Solution

**Sealed classes** and **sealed interfaces** define restricted class hierarchies where all subclasses must be declared in the same package and module. They enable the compiler to verify exhaustiveness in when expressions.

#### Basic Sealed Class

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

fun handleResult(result: Result<String>) {
    when (result) {
        is Result.Success -> println("Data: ${result.data}")
        is Result.Error -> println("Error: ${result.exception.message}")
        Result.Loading -> println("Loading...")
        // No else needed - exhaustive!
    }
}
```

#### Sealed Interface (Kotlin 1.5+)

```kotlin
sealed interface UiState

data class Loading(val progress: Int) : UiState
data class Success(val data: List<String>) : UiState
data class Error(val message: String) : UiState

// Can implement multiple sealed interfaces
sealed interface Loadable
sealed interface Refreshable

data class Content(val items: List<String>) : UiState, Loadable, Refreshable
```

#### Sealed Class vs Sealed Interface

```kotlin
// Sealed class: single inheritance
sealed class Animal {
    abstract val name: String
    data class Dog(override val name: String, val breed: String) : Animal()
    data class Cat(override val name: String, val color: String) : Animal()
}

// Sealed interface: multiple inheritance
sealed interface Clickable {
    fun onClick()
}

sealed interface Swipeable {
    fun onSwipe()
}

data class Button(val label: String) : Clickable {
    override fun onClick() = println("Button clicked")
}

data class Card(val content: String) : Clickable, Swipeable {
    override fun onClick() = println("Card clicked")
    override fun onSwipe() = println("Card swiped")
}
```

#### Exhaustive When Expression

```kotlin
sealed class Operation {
    data class Add(val value: Int) : Operation()
    data class Subtract(val value: Int) : Operation()
    data class Multiply(val value: Int) : Operation()
    data class Divide(val value: Int) : Operation()
}

fun calculate(initial: Int, operations: List<Operation>): Int {
    var result = initial
    for (op in operations) {
        result = when (op) {
            is Operation.Add -> result + op.value
            is Operation.Subtract -> result - op.value
            is Operation.Multiply -> result * op.value
            is Operation.Divide -> result / op.value
            // Compiler ensures all cases are handled
        }
    }
    return result
}
```

#### Sealed vs Enum

```kotlin
// Enum: Fixed set of constants
enum class Direction {
    NORTH, SOUTH, EAST, WEST;

    fun opposite() = when (this) {
        NORTH -> SOUTH
        SOUTH -> NORTH
        EAST -> WEST
        WEST -> EAST
    }
}

// Sealed: Each subclass can have different properties
sealed class Result {
    data class Success(val data: String, val timestamp: Long) : Result()
    data class Error(val exception: Exception, val retryable: Boolean) : Result()
    object Loading : Result()
}

// Enum for simple cases, Sealed for complex hierarchies
```

#### Nested Hierarchies

```kotlin
sealed class NetworkResult<out T> {
    data class Success<T>(val data: T, val cached: Boolean) : NetworkResult<T>()

    sealed class Error : NetworkResult<Nothing>() {
        data class HttpError(val code: Int, val message: String) : Error()
        data class NetworkError(val exception: Exception) : Error()
        object Timeout : Error()
        object NoConnection : Error()
    }

    object Loading : NetworkResult<Nothing>()
}

fun handleNetworkResult(result: NetworkResult<String>) {
    when (result) {
        is NetworkResult.Success -> println("Data: ${result.data}")
        is NetworkResult.Error.HttpError -> println("HTTP ${result.code}")
        is NetworkResult.Error.NetworkError -> println("Network error")
        NetworkResult.Error.Timeout -> println("Timeout")
        NetworkResult.Error.NoConnection -> println("No connection")
        NetworkResult.Loading -> println("Loading")
    }
}
```

### Best Practices

1. **Use sealed classes for restricted hierarchies**
2. **Use sealed interfaces for multiple inheritance**
3. **Leverage exhaustive when expressions**
4. **Prefer sealed over enum for complex data**
5. **Keep sealed hierarchies in same file for clarity**

---

## Русский

[Full translation...]

---

## Follow-ups

1. Can sealed classes have protected constructors?
2. How do sealed classes work across different modules?
3. What's the performance difference between sealed classes and enums?
4. Can you use sealed classes with generics effectively?
5. How do sealed interfaces differ in Java interop?

## References

- [Kotlin Sealed Classes](https://kotlinlang.org/docs/sealed-classes.html)
- [Kotlin 1.5 Release - Sealed Interfaces](https://kotlinlang.org/docs/whatsnew15.html#sealed-interfaces)

## Related Questions

- [[q-enum-class-advanced--kotlin--medium]]
- [[q-data-class-detailed--kotlin--medium]]
- [[q-inheritance-open-final--kotlin--medium]]

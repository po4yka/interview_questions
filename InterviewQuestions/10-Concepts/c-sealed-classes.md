---
id: ivc-20251030-122934
title: Sealed Classes / Запечатанные классы
aliases: [Kotlin Sealed, Sealed Class Hierarchy, Sealed Classes, Запечатанные классы]
kind: concept
summary: Kotlin sealed classes for restricted class hierarchies enabling exhaustive when expressions
links: []
created: 2025-10-30
updated: 2025-10-30
tags: [adt, concept, exhaustive-when, kotlin, sealed-classes, type-safety]
date created: Thursday, October 30th 2025, 12:30:04 pm
date modified: Saturday, November 1st 2025, 5:43:38 pm
---

# Summary (EN)

Sealed classes in Kotlin define **restricted class hierarchies** where all subclasses must be declared in the same file (or package in Kotlin 1.5+). This creates a closed set of types known at compile time, enabling exhaustive `when` expressions without an `else` branch. Sealed classes are ideal for representing **finite state machines**, **result types**, and **algebraic data types (ADTs)** where you need type-safe, compiler-verified handling of all possible cases.

**Key Benefits**:
- Compile-time exhaustiveness checking in when expressions
- More flexible than enums (each subclass can have different data)
- Type-safe state representation
- Prevents external implementations

# Сводка (RU)

Запечатанные классы (sealed classes) в Kotlin определяют **ограниченные иерархии классов**, где все подклассы должны быть объявлены в том же файле (или пакете в Kotlin 1.5+). Это создает закрытый набор типов, известных на этапе компиляции, что позволяет использовать исчерпывающие `when`-выражения без ветки `else`. Sealed-классы идеальны для представления **конечных автоматов**, **типов результатов** и **алгебраических типов данных (ADT)**, где требуется типобезопасная обработка всех возможных случаев с проверкой компилятором.

**Ключевые преимущества**:
- Проверка исчерпываемости в when-выражениях на этапе компиляции
- Более гибкие, чем enum (каждый подкласс может иметь разные данные)
- Типобезопасное представление состояний
- Предотвращение внешних реализаций

---

## Core Concept

**Closed Type Hierarchy**: Sealed classes restrict inheritance to a known set of subtypes. The compiler knows all possible subclasses, enabling exhaustive pattern matching.

**vs Regular Abstract Classes**: Regular abstract/open classes can be extended anywhere in the codebase. Sealed classes limit subclasses to the same compilation unit.

**vs Enum Classes**: Enums have fixed instances with identical structure. Sealed classes allow each subclass to have different properties and constructors.

```kotlin
// Sealed class - restricted hierarchy
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Exhaustive when - no else needed
fun <T> handleResult(result: Result<T>) = when (result) {
    is Result.Success -> println("Data: ${result.data}")
    is Result.Error -> println("Error: ${result.exception.message}")
    Result.Loading -> println("Loading...")
    // Compiler error if any case is missing
}
```

## Use Cases / Trade-offs

**Primary Use Cases**:

1. **UI State Representation**
```kotlin
sealed class UiState {
    object Idle : UiState()
    object Loading : UiState()
    data class Success(val data: List<Item>) : UiState()
    data class Error(val message: String) : UiState()
}
```

2. **Network Response Modeling**
```kotlin
sealed class ApiResponse<out T> {
    data class Success<T>(val body: T, val code: Int = 200) : ApiResponse<T>()
    data class Error(val code: Int, val message: String) : ApiResponse<Nothing>()
    object NetworkError : ApiResponse<Nothing>()
}
```

3. **Navigation Events**
```kotlin
sealed class NavigationEvent {
    object NavigateBack : NavigationEvent()
    data class NavigateToDetail(val id: String) : NavigationEvent()
    data class NavigateToUrl(val url: String) : NavigationEvent()
}
```

4. **Algebraic Data Types (ADTs)**
```kotlin
sealed class Expression {
    data class Const(val value: Int) : Expression()
    data class Add(val left: Expression, val right: Expression) : Expression()
    data class Multiply(val left: Expression, val right: Expression) : Expression()
}

fun eval(expr: Expression): Int = when (expr) {
    is Expression.Const -> expr.value
    is Expression.Add -> eval(expr.left) + eval(expr.right)
    is Expression.Multiply -> eval(expr.left) * eval(expr.right)
}
```

**Trade-offs**:

| Aspect | Sealed Classes | Enums | Open Classes |
|--------|---------------|-------|-------------|
| Flexibility | High (different data per type) | Low (fixed instances) | Highest (unlimited) |
| Safety | Exhaustive checking | Exhaustive checking | No compile-time safety |
| Extensibility | Restricted to file/package | Cannot extend | Unlimited extension |
| Performance | Negligible overhead | Most efficient | Standard |

**Best Practices**:
- Use sealed classes for finite, well-defined state spaces
- Prefer sealed classes over error codes or string constants
- Combine with data classes for immutable state representations
- Use object for singleton states (Loading, Idle)
- Avoid deeply nested sealed hierarchies (keep it 1-2 levels)

**When NOT to Use**:
- Open-ended hierarchies that may grow across modules
- Plugin architectures requiring external extensions
- When enum with properties suffices

## References

- [Kotlin Docs: Sealed Classes](https://kotlinlang.org/docs/sealed-classes.html)
- [Effective Kotlin: Use sealed classes to represent state](https://kt.academy/article/ek-sealed-classes)
- [[c-kotlin-when-expression]] - Exhaustive when expressions
- [[c-adt]] - Algebraic Data Types pattern
- Related: [[q-sealed-vs-enum--kotlin--medium]]

---
id: cs-010
title: "Why Data and Sealed Classes / Зачем Data и Sealed Classes"
aliases: ["Why Data and Sealed Classes", "Зачем Data и Sealed Classes"]
topic: cs
subtopics: [data-classes, kotlin, programming-languages, sealed-classes]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-sealed-classes]
created: 2025-10-15
updated: 2025-01-25
tags: [data-class, difficulty/medium, kotlin, programming-languages, sealed-classes]
sources: [https://kotlinlang.org/docs/sealed-classes.html]
---

# Вопрос (RU)
> Зачем нужны Data Class и Sealed Classes? Какие проблемы они решают?

# Question (EN)
> Why do we need Data Classes and Sealed Classes? What problems do they solve?

---

## Ответ (RU)

**Теория Data и Sealed Classes:**
Data Classes автоматически генерируют 5 методов (equals, hashCode, toString, copy, componentN), уменьшая boilerplate для value objects. Sealed Classes определяют закрытые иерархии с ограниченным набором подтипов. Они решают разные проблемы: Data Classes - хранение данных и immutability, Sealed Classes - безопасное state management и exhaustive when expressions.

**Зачем нужны Data Classes:**

*Теория:* Data Classes решают проблему boilerplate в value objects. В Java/C# нужно вручную писать equals/hashCode/toString для каждого класса. Data Classes автоматически генерируют эти методы на основе properties в primary constructor. Используются для DTOs, API responses, database entities, immutable state.

```kotlin
// ✅ Data Class - автоматическая генерация методов
data class User(val name: String, val age: Int) {
    // Компилятор автоматически генерирует:
    // - equals()
    // - hashCode()
    // - toString()
    // - copy()
    // - componentN()
}

// Сравнение с обычным классом
val user1 = User("Alice", 30)
val user2 = User("Alice", 30)
println(user1 == user2)  // true - сравнение по содержимому
println(user1.copy(age = 31))  // User(name=Alice, age=31)
val (name, age) = user1  // destructuring
```

**Использование Data Classes:**

*Теория:* Data Classes идеальны для value objects без бизнес-логики. Используются для передачи данных между слоями (MVP/MVVM), API responses, database entities, immutable state. `copy()` поддерживает immutability pattern - создание модифицированных копий вместо изменения оригинала.

```kotlin
// ✅ DTO для API
data class ApiResponse<T>(
    val success: Boolean,
    val data: T?,
    val message: String
)

// ✅ State management
data class UiState(
    val isLoading: Boolean,
    val data: List<Item>?,
    val error: String?
)

// ✅ Immutability pattern
val state = UiState(false, listOf(Item()), null)
val loadingState = state.copy(isLoading = true)  // Новая копия
```

**Зачем нужны Sealed Classes:**

*Теория:* Sealed Classes решают проблему ограниченных иерархий. Заменили устаревшие enum classes с data. Обеспечивают exhaustiveness в when expressions - все подтипы должны быть обработаны. Позволяют разные properties для разных подтипов. Используются для state machines, Result types, UI states, navigation states.

```kotlin
// ✅ Sealed Class для state management
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Exhaustive when - компилятор требует обработку всех cases
fun handleResult(result: Result<String>) {
    when (result) {
        is Result.Success -> println("Data: ${result.data}")
        is Result.Error -> println("Error: ${result.message}")
        is Result.Loading -> println("Loading...")
        // Компилятор гарантирует, что все cases обработаны!
    }
}
```

**Sealed Classes vs Enum Classes:**

*Теория:* Enum classes - singleton instances с одинаковыми properties. Sealed classes - могут иметь разные properties для каждого подтипа. Sealed classes более гибкие для modeling state machines. Enum classes более ограничены, но более эффективны по памяти.

```kotlin
// ❌ Enum class - ограничен
enum class Status(val code: Int) {
    SUCCESS(200),
    ERROR(400),
    LOADING(0)  // Все instances имеют одинаковую структуру
}

// ✅ Sealed class - гибкость
sealed class Status {
    data class Success(val data: String) : Status()
    data class Error(val code: Int, val message: String) : Status()
    object Loading : Status()  // Разные properties для разных случаев
}

// Разные подтипы могут иметь разные данные
val status1 = Status.Success("Data")
val status2 = Status.Error(404, "Not Found")
val status3 = Status.Loading  // object instance
```

**Реальные примеры использования:**

*Теория:* Sealed classes используются для modeling bounded domains - когда список возможных значений ограничен и известен. API responses, UI states, navigation states, parsing results - типичные use cases.

```kotlin
// ✅ API Response handling
sealed class NetworkResponse<out T> {
    data class Success<T>(val data: T) : NetworkResponse<T>()
    data class Error(val code: Int, val message: String) : NetworkResponse<Nothing>()
    object Timeout : NetworkResponse<Nothing>()
    object NoConnection : NetworkResponse<Nothing>()
}

// ✅ UI State management
sealed class ScreenState {
    object Loading : ScreenState()
    data class Success(val items: List<Item>) : ScreenState()
    data class Error(val error: String) : ScreenState()
    data class Empty(val message: String) : ScreenState()
}

// ✅ Navigation state
sealed class NavigationEvent {
    data class NavigateTo(val route: String) : NavigationEvent()
    object GoBack : NavigationEvent()
    data class ShowDialog(val message: String) : NavigationEvent()
    object DismissDialog : NavigationEvent()
}
```

**Type Safety и Exhaustiveness:**

*Теория:* Sealed classes обеспечивают compile-time type safety. When expression проверяется компилятором на exhaustiveness - все подтипы должны быть обработаны. Это предотвращает runtime ошибки от пропущенных cases. Если добавлен новый подтип, компилятор требует обновления всех when expressions.

```kotlin
// ✅ Compile-time safety
sealed class TaskState {
    data class InProgress(val progress: Int) : TaskState()
    data class Completed(val result: Any) : TaskState()
    object Pending : TaskState()
}

fun handleState(state: TaskState) {
    when (state) {
        is TaskState.InProgress -> println("Progress: ${state.progress}")
        is TaskState.Completed -> println("Result: ${state.result}")
        is TaskState.Pending -> println("Waiting...")
        // Компилятор проверит, что все cases обработаны
    }
}

// Если добавить новый подтип:
sealed class TaskState {
    data class InProgress(val progress: Int) : TaskState()
    data class Completed(val result: Any) : TaskState()
    object Pending : TaskState()
    object Cancelled : TaskState()  // Новый подтип
}

// Компилятор выдаст warning/error для всех when expressions, которые не обрабатывают TaskState.Cancelled
```

**Ключевые концепции:**

1. **Boilerplate Reduction** - Data classes генерируют стандартные методы автоматически
2. **Immutability** - copy() поддерживает immutability pattern
3. **Type Safety** - Sealed classes обеспечивают compile-time type safety
4. **Exhaustiveness** - Компилятор гарантирует обработку всех подтипов
5. **Bounded Domains** - Sealed classes моделируют ограниченные иерархии

## Answer (EN)

**Data and Sealed Classes Theory:**
Data Classes automatically generate 5 methods (equals, hashCode, toString, copy, componentN), reducing boilerplate for value objects. Sealed Classes define closed hierarchies with limited set of subtypes. They solve different problems: Data Classes - data storage and immutability, Sealed Classes - safe state management and exhaustive when expressions.

**Why Data Classes:**

*Theory:* Data Classes solve boilerplate problem in value objects. In Java/C# need to manually write equals/hashCode/toString for each class. Data Classes automatically generate these methods based on properties in primary constructor. Used for DTOs, API responses, database entities, immutable state.

```kotlin
// ✅ Data Class - automatic method generation
data class User(val name: String, val age: Int) {
    // Compiler automatically generates:
    // - equals()
    // - hashCode()
    // - toString()
    // - copy()
    // - componentN()
}

// Comparison with regular class
val user1 = User("Alice", 30)
val user2 = User("Alice", 30)
println(user1 == user2)  // true - content comparison
println(user1.copy(age = 31))  // User(name=Alice, age=31)
val (name, age) = user1  // destructuring
```

**Data Classes Usage:**

*Theory:* Data Classes ideal for value objects without business logic. Used for passing data between layers (MVP/MVVM), API responses, database entities, immutable state. `copy()` supports immutability pattern - creating modified copies instead of changing original.

```kotlin
// ✅ DTO for API
data class ApiResponse<T>(
    val success: Boolean,
    val data: T?,
    val message: String
)

// ✅ State management
data class UiState(
    val isLoading: Boolean,
    val data: List<Item>?,
    val error: String?
)

// ✅ Immutability pattern
val state = UiState(false, listOf(Item()), null)
val loadingState = state.copy(isLoading = true)  // New copy
```

**Why Sealed Classes:**

*Theory:* Sealed Classes solve bounded hierarchies problem. Replaced deprecated enum classes with data. Ensure exhaustiveness in when expressions - all subtypes must be handled. Allow different properties for different subtypes. Used for state machines, Result types, UI states, navigation states.

```kotlin
// ✅ Sealed Class for state management
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Exhaustive when - compiler requires handling all cases
fun handleResult(result: Result<String>) {
    when (result) {
        is Result.Success -> println("Data: ${result.data}")
        is Result.Error -> println("Error: ${result.message}")
        is Result.Loading -> println("Loading...")
        // Compiler guarantees all cases handled!
    }
}
```

**Sealed Classes vs Enum Classes:**

*Theory:* Enum classes - singleton instances with same properties. Sealed classes - can have different properties for each subtype. Sealed classes more flexible for modeling state machines. Enum classes more limited, but more memory efficient.

```kotlin
// ❌ Enum class - limited
enum class Status(val code: Int) {
    SUCCESS(200),
    ERROR(400),
    LOADING(0)  // All instances have same structure
}

// ✅ Sealed class - flexibility
sealed class Status {
    data class Success(val data: String) : Status()
    data class Error(val code: Int, val message: String) : Status()
    object Loading : Status()  // Different properties for different cases
}

// Different subtypes can have different data
val status1 = Status.Success("Data")
val status2 = Status.Error(404, "Not Found")
val status3 = Status.Loading  // object instance
```

**Real-World Usage Examples:**

*Theory:* Sealed classes used for modeling bounded domains - when list of possible values limited and known. API responses, UI states, navigation states, parsing results - typical use cases.

```kotlin
// ✅ API Response handling
sealed class NetworkResponse<out T> {
    data class Success<T>(val data: T) : NetworkResponse<T>()
    data class Error(val code: Int, val message: String) : NetworkResponse<Nothing>()
    object Timeout : NetworkResponse<Nothing>()
    object NoConnection : NetworkResponse<Nothing>()
}

// ✅ UI State management
sealed class ScreenState {
    object Loading : ScreenState()
    data class Success(val items: List<Item>) : ScreenState()
    data class Error(val error: String) : ScreenState()
    data class Empty(val message: String) : ScreenState()
}

// ✅ Navigation state
sealed class NavigationEvent {
    data class NavigateTo(val route: String) : NavigationEvent()
    object GoBack : NavigationEvent()
    data class ShowDialog(val message: String) : NavigationEvent()
    object DismissDialog : NavigationEvent()
}
```

**Type Safety and Exhaustiveness:**

*Theory:* Sealed classes ensure compile-time type safety. When expression checked by compiler for exhaustiveness - all subtypes must be handled. This prevents runtime errors from missed cases. If new subtype added, compiler requires updating all when expressions.

```kotlin
// ✅ Compile-time safety
sealed class TaskState {
    data class InProgress(val progress: Int) : TaskState()
    data class Completed(val result: Any) : TaskState()
    object Pending : TaskState()
}

fun handleState(state: TaskState) {
    when (state) {
        is TaskState.InProgress -> println("Progress: ${state.progress}")
        is TaskState.Completed -> println("Result: ${state.result}")
        is TaskState.Pending -> println("Waiting...")
        // Compiler checks all cases handled
    }
}

// If add new subtype:
sealed class TaskState {
    data class InProgress(val progress: Int) : TaskState()
    data class Completed(val result: Any) : TaskState()
    object Pending : TaskState()
    object Cancelled : TaskState()  // New subtype
}

// Compiler will show warning/error for all when expressions not handling TaskState.Cancelled
```

**Key Concepts:**

1. **Boilerplate Reduction** - Data classes generate standard methods automatically
2. **Immutability** - copy() supports immutability pattern
3. **Type Safety** - Sealed classes ensure compile-time type safety
4. **Exhaustiveness** - Compiler guarantees handling all subtypes
5. **Bounded Domains** - Sealed classes model limited hierarchies

---

## Follow-ups

- When should you use data class vs sealed class?
- Can a sealed class have sealed subclasses?
- How do you test exhaustiveness in when expressions?

## Related Questions

### Prerequisites (Easier)
- [[q-data-class-special-features--programming-languages--easy]] - Data classes basics

### Related (Same Level)
- [[q-sealed-classes--kotlin--medium]] - Sealed classes details

### Advanced (Harder)
- Advanced sealed class hierarchies
- Custom equals/hashCode for sealed classes

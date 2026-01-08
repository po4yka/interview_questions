---id: cs-010
title: "Why Data and Sealed Classes / Зачем Data и Sealed Classes"
aliases: ["Why Data and Sealed Classes", "Зачем Data и Sealed Classes"]
topic: cs
subtopics: [data-classes, kotlin, sealed-classes]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-aggregation, c-app-signing, c-backend, c-binary-search, c-binary-search-tree, c-binder, c-biometric-authentication, c-bm25-ranking, c-by-type, c-cap-theorem, c-ci-cd, c-ci-cd-pipelines, c-clean-code, c-compiler-optimization, c-compose-modifiers, c-compose-phases, c-compose-semantics, c-computer-science, c-concurrency, c-cross-platform-development, c-cross-platform-mobile, c-cs, c-data-classes, c-data-loading, c-debugging, c-declarative-programming, c-deep-linking, c-density-independent-pixels, c-dimension-units, c-dp-sp-units, c-dsl-builders, c-dynamic-programming, c-espresso-testing, c-event-handling, c-folder, c-functional-programming, c-gdpr-compliance, c-gesture-detection, c-gradle-build-cache, c-gradle-build-system, c-https-tls, c-image-formats, c-inheritance, c-jit-aot-compilation, c-kmm, c-kotlin, c-lambda-expressions, c-lazy-grid, c-lazy-initialization, c-level, c-load-balancing, c-manifest, c-memory-optimization, c-memory-profiler, c-microservices, c-multipart-form-data, c-multithreading, c-mutablestate, c-networking, c-offline-first-architecture, c-oop, c-oop-concepts, c-oop-fundamentals, c-oop-principles, c-play-console, c-play-feature-delivery, c-programming-languages, c-properties, c-real-time-communication, c-references, c-scaling-strategies, c-scoped-storage, c-security, c-serialization, c-server-sent-events, c-shader-programming, c-snapshot-system, c-specific, c-strictmode, c-system-ui, c-test-doubles, c-test-sharding, c-testing-pyramid, c-testing-strategies, c-theming, c-to-folder, c-token-management, c-touch-input, c-turbine-testing, c-two-pointers, c-ui-testing, c-ui-ux-accessibility, c-value-classes, c-variable, c-weak-references, c-windowinsets, c-xml, q-sealed-classes--kotlin--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [data-classes, difficulty/medium, kotlin, programming-languages, sealed-classes]
sources: ["https://kotlinlang.org/docs/sealed-classes.html"]
---
# Вопрос (RU)
> Зачем нужны Data Class и Sealed Classes? Какие проблемы они решают?

# Question (EN)
> Why do we need Data Classes and Sealed Classes? What problems do they solve?

---

## Ответ (RU)

**Теория Data и Sealed Classes:**
Data Classes автоматически генерируют 5 методов (`equals`, `hashCode`, `toString`, `copy`, `componentN`), уменьшая boilerplate для value objects. Sealed Classes определяют закрытые иерархии с ограниченным набором подтипов. Они решают разные проблемы: Data Classes — удобное хранение и передачу данных (часто в неизменяемом виде), Sealed Classes — типобезопасное моделирование ограниченных состояний и поддержку исчерпывающих `when`-выражений.

**Зачем нужны Data Classes:**

*Теория:* Data Classes решают проблему boilerplate в value objects. В Java/C# нужно вручную писать `equals`/`hashCode`/`toString` для каждого класса. Data Classes автоматически генерируют эти методы на основе properties в primary constructor. Идеальны для классов, где идентичность определяется данными. Часто используются для DTO, API responses, database entities, immutable state. Важно: неизменяемость достигается по соглашению (использованием `val` и отсутствием изменяемого состояния), а не навязывается самим `data class`.

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

*Теория:* Data Classes идеальны для value objects без сложной бизнес-логики. Используются для передачи данных между слоями (MVP/MVVM), API responses, database entities, immutable state. `copy()` поддерживает immutability pattern — создание модифицированных копий вместо изменения оригинала.

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

*Теория:* Sealed Classes решают проблему моделирования ограниченных иерархий типов. Они являются более гибкой альтернативой enum, когда для разных вариантов нужны разные данные и поведение. Обеспечивают поддержку исчерпывающих `when`-выражений (когда все подтипы известны и видны в данной компиляционной единице). Позволяют разные properties для разных подтипов. Используются для state machines, Result types, UI states, navigation states.

```kotlin
// ✅ Sealed Class для state management
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Exhaustive when - при известных всех подтипах компилятор может потребовать обработку всех cases
fun handleResult(result: Result<String>) {
    when (result) {
        is Result.Success -> println("Data: ${result.data}")
        is Result.Error -> println("Error: ${result.message}")
        is Result.Loading -> println("Loading...")
        // Если добавить новый подтип Result, компилятор подсветит не-исчерпывающие when-выражения
    }
}
```

**Sealed Classes vs Enum Classes:**

*Теория:* Enum classes — набор однотипных singleton-экземпляров с общей структурой. Sealed classes — семейство подтипов, каждый из которых может иметь собственные свойства и (при необходимости) состояние. Sealed classes более гибки для моделирования сложных конечных автоматов и состояний. Enum classes более просты и могут быть эффективнее по памяти для небольших фиксированных наборов значений.

```kotlin
// Enum class - ограничен, но подходит для простых фиксированных наборов
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

*Теория:* Sealed classes используются для моделирования bounded domains — когда список возможных вариантов ограничен и известен во время компиляции.

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

*Теория:* Sealed classes обеспечивают сильную типобезопасность: все допустимые варианты состояния явно моделируются подтипами. `when`-выражения по sealed class могут проверяться компилятором на исчерпывающий разбор (при использовании как выражения и при видимости всех подтипов). Это помогает обнаруживать пропущенные варианты на этапе компиляции. При добавлении нового подтипа компилятор подсветит `when`, которые больше не являются исчерпывающими.

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
        // Компилятор может проверить исчерпываемость when при известных всех подтипах
    }
}

// Если к иерархии добавить новый подтип:
sealed class TaskState {
    data class InProgress(val progress: Int) : TaskState()
    data class Completed(val result: Any) : TaskState()
    object Pending : TaskState()
    object Cancelled : TaskState()  // Новый подтип
}

// Тогда when-выражения вида `when(state: TaskState) = ...` без ветки для Cancelled
// станут не-исчерпывающими, и компилятор сообщит об этом (warning/error в зависимости от контекста).
```

**Ключевые концепции:**

1. Boilerplate Reduction — Data classes генерируют стандартные методы автоматически.
2. Immutability — `copy()` упрощает следование immutability-подходу (иммутабельность достигается через `val` и дизайн).
3. Type Safety — Sealed classes обеспечивают типобезопасное моделирование закрытых иерархий.
4. Exhaustiveness — Компилятор может гарантировать обработку всех подтипов в `when` при соблюдении условий исчерпываемости.
5. Bounded Domains — Sealed classes моделируют ограниченные домены и конечные множества состояний.

## Answer (EN)

**Data and Sealed Classes Theory:**
Data Classes automatically generate 5 methods (`equals`, `hashCode`, `toString`, `copy`, `componentN`), reducing boilerplate for value objects. Sealed Classes define closed hierarchies with a limited set of subtypes. They solve different problems: Data Classes — convenient data holding and transfer (often in an immutable style), Sealed Classes — type-safe modeling of bounded states and support for exhaustive `when` expressions.

**Why Data Classes:**

*Theory:* Data Classes solve the boilerplate problem for value objects. In Java/C# you need to manually write `equals`/`hashCode`/`toString` for each class. Data Classes automatically generate these methods based on properties in the primary constructor. They are ideal when identity is defined by data. Commonly used for DTOs, API responses, database entities, immutable state. Note: immutability is achieved by convention (using `val` and avoiding mutable state), not enforced by the `data class` keyword itself.

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

*Theory:* Data Classes are ideal for value objects without complex business logic. Used for passing data between layers (MVP/MVVM), API responses, database entities, immutable state. `copy()` supports an immutability pattern — creating modified copies instead of mutating the original instance.

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

*Theory:* Sealed Classes solve the problem of modeling bounded type hierarchies. They are a more flexible alternative to enums when different variants need different data and behavior. They enable support for exhaustive `when` expressions when all subtypes are known and visible to the compiler. They allow different properties for different subtypes. Used for state machines, Result types, UI states, navigation states.

```kotlin
// ✅ Sealed Class for state management
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Exhaustive when - when all subtypes are known, the compiler can require handling all cases
fun handleResult(result: Result<String>) {
    when (result) {
        is Result.Success -> println("Data: ${result.data}")
        is Result.Error -> println("Error: ${result.message}")
        is Result.Loading -> println("Loading...")
        // If a new Result subtype is added, non-exhaustive when-expressions will be reported by the compiler
    }
}
```

**Sealed Classes vs Enum Classes:**

*Theory:* Enum classes are sets of singleton instances sharing the same structure. Sealed classes define a family of subtypes where each can have its own properties and (if needed) state. Sealed classes are more flexible for modeling complex state machines. Enum classes are simpler and can often be more memory-efficient for small fixed sets of values.

```kotlin
// Enum class - limited but great for simple fixed sets
enum class Status(val code: Int) {
    SUCCESS(200),
    ERROR(400),
    LOADING(0)  // All instances have the same structure
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

*Theory:* Sealed classes are used for modeling bounded domains — when the list of possible variants is limited and known at compile time.

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

*Theory:* Sealed classes provide strong type safety: all valid variants are explicitly modeled as subtypes. `when` expressions over sealed classes can be checked by the compiler for exhaustiveness (when used as expressions and when all subtypes are visible), which helps catch missing cases at compile time. When a new subtype is added, existing exhaustive `when` expressions that do not handle it become non-exhaustive and are reported.

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
        // The compiler can verify exhaustiveness when all subtypes are known
    }
}

// Conceptually, if you extend the hierarchy with a new subtype:
sealed class TaskState {
    data class InProgress(val progress: Int) : TaskState()
    data class Completed(val result: Any) : TaskState()
    object Pending : TaskState()
    object Cancelled : TaskState()  // New subtype
}

// then `when (state: TaskState) { ... }` expressions without a branch for Cancelled
// become non-exhaustive and the compiler reports this (warning/error depending on context).
```

**Key Concepts:**

1. Boilerplate Reduction - Data classes generate standard methods automatically.
2. Immutability - `copy()` facilitates an immutability pattern (immutability is by design, not enforced).
3. Type Safety - Sealed classes provide type-safe modeling of closed hierarchies.
4. Exhaustiveness - The compiler can guarantee handling all subtypes in `when` expressions when exhaustiveness conditions are met.
5. Bounded Domains - Sealed classes model limited domains and finite sets of states.

---

## Дополнительные Вопросы (RU)

- Когда следует использовать `data class`, а когда `sealed class`?
- Может ли sealed class иметь sealed-подклассы?
- Как проверить исчерпываемость `when`-выражений на практике?

## Follow-ups

- When should you use data class vs sealed class?
- Can a sealed class have sealed subclasses?
- How do you test exhaustiveness in when expressions in practice?

## Связанные Вопросы (RU)

### База (проще)
- Основы data classes и их особенности

### На Том Же Уровне
- [[q-sealed-classes--kotlin--medium]] - Детали sealed classes

### Сложнее
- Продвинутые иерархии sealed classes
- Кастомные `equals`/`hashCode` для sealed classes

## Related Questions

### Prerequisites (Easier)
- Data classes basics

### Related (Same Level)
- [[q-sealed-classes--kotlin--medium]] - Sealed classes details

### Advanced (Harder)
- Advanced sealed class hierarchies
- Custom equals/hashCode for sealed classes

## References

- [[c-computer-science]]
- "https://kotlinlang.org/docs/sealed-classes.html"

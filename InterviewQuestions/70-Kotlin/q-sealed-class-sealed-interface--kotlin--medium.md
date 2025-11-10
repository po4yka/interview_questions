---
id: kotlin-113
title: "Sealed classes vs sealed interfaces in Kotlin / Sealed классы vs интерфейсы"
aliases: [Polymorphism, Sealed Classes, Sealed Interfaces, Sealed v Kotlin]
topic: kotlin
subtopics: [sealed-classes, classes, polymorphism]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-sealed-classes, c-kotlin, q-kotlin-enum-classes--kotlin--easy]
created: 2025-10-12
updated: 2025-11-09
tags: [classes, difficulty/medium, kotlin, polymorphism, sealed-classes, sealed-interfaces, when-expression]
---

# Вопрос (RU)

> В чем различия между sealed классами и sealed интерфейсами в Kotlin, как они используются, и как они соотносятся с enum?

## Ответ (RU)

**Sealed классы** и **sealed интерфейсы** определяют ограниченные иерархии типов, где все непосредственно наследующие типы должны быть объявлены в том же пакете (и, в зависимости от таргета/платформы, в рамках той же единицы компиляции). Это позволяет компилятору проверять полноту `when` выражений.

#### Базовый Sealed Класс

```kotlin
sealed class Result<out T> {
    data class Success<out T>(val data: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

fun handleResult(result: Result<String>) {
    when (result) {
        is Result.Success -> println("Данные: ${result.data}")
        is Result.Error -> println("Ошибка: ${result.exception.message}")
        Result.Loading -> println("Загрузка...")
        // else не нужен - выражение исчерпывающее
    }
}
```

#### Sealed Интерфейс (Kotlin 1.5+)

```kotlin
sealed interface UiState

data class Loading(val progress: Int) : UiState
data class Success(val data: List<String>) : UiState
data class Error(val message: String) : UiState

// Класс может реализовывать несколько sealed интерфейсов
sealed interface Loadable
sealed interface Refreshable

data class Content(val items: List<String>) : UiState, Loadable, Refreshable
```

#### Sealed Класс Vs Sealed Интерфейс

```kotlin
// Sealed класс: одиночное наследование
sealed class Animal {
    abstract val name: String
    data class Dog(override val name: String, val breed: String) : Animal()
    data class Cat(override val name: String, val color: String) : Animal()
}

// Sealed интерфейс: множественное наследование
sealed interface Clickable {
    fun onClick()
}

sealed interface Swipeable {
    fun onSwipe()
}

data class Button(val label: String) : Clickable {
    override fun onClick() = println("Кнопка нажата")
}

data class Card(val content: String) : Clickable, Swipeable {
    override fun onClick() = println("Карточка нажата")
    override fun onSwipe() = println("Карточка свайпнута")
}
```

#### Exhaustive when Выражение

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
            // Компилятор гарантирует обработку всех вариантов (else не нужен)
        }
    }
    return result
}
```

#### Sealed Vs Enum

```kotlin
// Enum: фиксированный набор констант одного типа
enum class Direction {
    NORTH, SOUTH, EAST, WEST;

    fun opposite() = when (this) {
        NORTH -> SOUTH
        SOUTH -> NORTH
        EAST -> WEST
        WEST -> EAST
    }
}

// Sealed: каждый подкласс может иметь свои свойства и поведение
sealed class Result2 {
    data class Success(val data: String, val timestamp: Long) : Result2()
    data class Error(val exception: Exception, val retryable: Boolean) : Result2()
    object Loading : Result2()
}

// Enum — для простых и обычно однотипных состояний; sealed — для сложных, неоднородных иерархий
```

#### Вложенные Иерархии

```kotlin
sealed class NetworkResult<out T> {
    data class Success<out T>(val data: T, val cached: Boolean) : NetworkResult<T>()

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
        is NetworkResult.Success -> println("Данные: ${result.data}")
        is NetworkResult.Error.HttpError -> println("HTTP ${result.code}")
        is NetworkResult.Error.NetworkError -> println("Сетевая ошибка")
        NetworkResult.Error.Timeout -> println("Тайм-аут")
        NetworkResult.Error.NoConnection -> println("Нет соединения")
        NetworkResult.Loading -> println("Загрузка")
    }
}
```

### Ключевые Различия

| Аспект | Sealed класс | Sealed интерфейс | Enum |
|--------|--------------|------------------|------|
| Наследование | Одиночное | Множественное (можно реализовать несколько интерфейсов) | Нет (каждый enum — финальный элемент) |
| Свойства | Разные для подклассов | Разные для реализаций | Общие поля/методы типа, entries могут иметь свои параметры/реализацию |
| Когда использовать | Иерархия типов | Композиция поведений и контрактов | Простые фиксированные константы |
| Exhaustive `when` | Да | Да | Да |
| Версия Kotlin | 1.0+ | 1.5+ | 1.0+ |

### Краткое Резюме

**Sealed классы и интерфейсы** ограничивают иерархии типов, обеспечивая:
- Exhaustive `when` выражения (компилятор проверяет полноту)
- Известный на этапе компиляции набор подтипов
- Типобезопасность

**Различия:**
- Sealed класс: одиночное наследование, может содержать реализацию и состояние.
- Sealed интерфейс: разрешает множественное наследование, задает контракты (без хранения состояния по умолчанию).

**Используйте для:**
- UI состояний (Loading, Success, Error)
- Result/Response типов для API
- Command/Event паттернов
- Навигационных состояний

# Question (EN)

> What are the differences between sealed classes and sealed interfaces in Kotlin, how are they used, and how do they compare to enums?

## Answer (EN)

**Sealed classes** and **sealed interfaces** define restricted class hierarchies where all directly inheriting types must be declared in the same package (and, depending on the target/platform, within the same compilation unit). They enable the compiler to verify exhaustiveness in `when` expressions.

#### Basic Sealed Class

```kotlin
sealed class Result<out T> {
    data class Success<out T>(val data: T) : Result<T>()
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

#### Sealed Class Vs Sealed Interface

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
            // Compiler ensures all cases are handled (no else needed)
        }
    }
    return result
}
```

#### Sealed Vs Enum

```kotlin
// Enum: Fixed set of constants with uniform type
enum class Direction {
    NORTH, SOUTH, EAST, WEST;

    fun opposite() = when (this) {
        NORTH -> SOUTH
        SOUTH -> NORTH
        EAST -> WEST
        WEST -> EAST
    }
}

// Sealed: Each subclass can have different properties and behaviour
sealed class Result2 {
    data class Success(val data: String, val timestamp: Long) : Result2()
    data class Error(val exception: Exception, val retryable: Boolean) : Result2()
    object Loading : Result2()
}

// Enum for simple, usually uniform cases; sealed for complex, heterogeneous hierarchies
```

#### Nested Hierarchies

```kotlin
sealed class NetworkResult<out T> {
    data class Success<out T>(val data: T, val cached: Boolean) : NetworkResult<T>()

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

### Key Differences

| Aspect | Sealed class | Sealed interface | Enum |
|--------|--------------|------------------|------|
| Inheritance | Single | Multiple (can implement several interfaces) | None (each enum entry is final) |
| Properties | Different per subclass | Different per implementation | Common type-level members; entries can have their own params/implementation |
| When to use | Type hierarchies | Composition of behaviours/contracts | Simple fixed constants |
| Exhaustive `when` | Yes | Yes | Yes |
| Kotlin version | 1.0+ | 1.5+ | 1.0+ |

### Summary

**Sealed classes and interfaces** restrict type hierarchies, providing:
- Exhaustive `when` expressions (compiler-checked)
- Compile-time known set of subtypes
- Type safety

**Differences:**
- Sealed class: single inheritance, can hold state and implementation.
- Sealed interface: supports multiple inheritance, defines contracts (no state by default).

**Use them for:**
- UI state (Loading, Success, Error)
- Result/Response types for APIs
- Command/Event patterns
- Navigation states

## Дополнительные вопросы (RU)

1. Могут ли sealed классы иметь `protected` конструкторы?
2. Как работают sealed классы при разделении иерархии по разным модулям?
3. Есть ли различия в производительности между sealed классами и enum?
4. Насколько эффективно использовать sealed классы с дженериками?
5. Как sealed интерфейсы ведут себя при интеропе с Java?

## Follow-ups

1. Can sealed classes have `protected` constructors?
2. How do sealed classes work across different modules?
3. What's the performance difference between sealed classes and enums?
4. Can you use sealed classes with generics effectively?
5. How do sealed interfaces differ in Java interop?

## Ссылки (RU)

- [Kotlin Sealed Classes](https://kotlinlang.org/docs/sealed-classes.html)
- [Kotlin 1.5 Release - Sealed Interfaces](https://kotlinlang.org/docs/whatsnew15.html#sealed-interfaces)
- [[c-sealed-classes]]

## References

- [Kotlin Sealed Classes](https://kotlinlang.org/docs/sealed-classes.html)
- [Kotlin 1.5 Release - Sealed Interfaces](https://kotlinlang.org/docs/whatsnew15.html#sealed-interfaces)
- [[c-sealed-classes]]

## Связанные вопросы (RU)

- [[q-enum-class-advanced--kotlin--medium]]
- [[q-data-class-detailed--kotlin--medium]]
- [[q-inheritance-open-final--kotlin--medium]]

## Related Questions

- [[q-enum-class-advanced--kotlin--medium]]
- [[q-data-class-detailed--kotlin--medium]]
- [[q-inheritance-open-final--kotlin--medium]]

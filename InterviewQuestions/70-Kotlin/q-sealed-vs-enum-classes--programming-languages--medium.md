---
id: lang-043
title: "Sealed Vs Enum Classes / Sealed против Enum Классов"
aliases: [Sealed Vs Enum Classes, Sealed против Enum Классов]
topic: programming-languages
subtopics: [class-hierarchy, enum, oop, sealed-classes]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-programming-languages
related: [q-primitive-vs-reference-types--programming-languages--easy, q-suspend-function-suspension-mechanism--programming-languages--hard, q-what-is-garbage-in-gc--programming-languages--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [comparison, difficulty/medium, enum, kotlin, oop, programming-languages, sealed-class]
date created: Friday, October 3rd 2025, 6:48:06 pm
date modified: Saturday, November 1st 2025, 5:43:23 pm
---

# Каковы Отличия Sealed И Enum Классов В Kotlin?

# Question (EN)
> What are the differences between sealed and enum classes in Kotlin?

# Вопрос (RU)
> Каковы отличия sealed и enum классов в Kotlin?

---

## Answer (EN)

### Key Differences

| Feature | Enum Class | Sealed Class |
|---------|-----------|--------------|
| **Structure** | Fixed set of homogeneous objects | Restricted class hierarchy |
| **Instance count** | Fixed at compile time | Can create multiple instances |
| **Properties** | All instances have same structure | Subclasses can have different properties |
| **Inheritance** | Cannot have subclasses | Can have multiple subclasses |
| **Use case** | Simple fixed values | Complex states with different data |

### Enum Class

**Fixed set of homogeneous objects with identical structure:**

```kotlin
enum class Color(val rgb: Int) {
    RED(0xFF0000),
    GREEN(0x00FF00),
    BLUE(0x0000FF);

    fun hex() = "#${rgb.toString(16)}"
}

// Usage
val color = Color.RED
println(color.rgb)  // 16711680
println(color.hex()) // #ff0000

// All enum instances have same structure
when (color) {
    Color.RED -> println("Red")
    Color.GREEN -> println("Green")
    Color.BLUE -> println("Blue")
    // Exhaustive: compiler knows all values
}
```

**Characteristics:**
- Each value is a single instance
- All values have same properties
- Cannot create new instances at runtime
- Can iterate over all values: `Color.values()`

### Sealed Class

**Restricted hierarchy where subclasses can have different structures:**

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T, val timestamp: Long) : Result<T>()
    data class Error(val exception: Exception, val code: Int) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Usage - different properties per subclass
val result: Result<User> = Result.Success(user, System.currentTimeMillis())

when (result) {
    is Result.Success -> println("Data: ${result.data}, time: ${result.timestamp}")
    is Result.Error -> println("Error: ${result.exception.message}, code: ${result.code}")
    is Result.Loading -> println("Loading...")
    // Exhaustive: compiler knows all subclasses
}

// Can create multiple Success instances with different data
val result1 = Result.Success("data1", 123L)
val result2 = Result.Success("data2", 456L)
```

**Characteristics:**
- Multiple instances of each subclass allowed
- Subclasses can have completely different properties
- Can have data classes, objects, regular classes as subclasses
- Cannot create instances of sealed class itself

### When to Use Each

**Use `enum class` when:**
- Fixed set of values that won't change
- All values have same structure
- Simple states or constants
- Need to iterate over all values

```kotlin
enum class Direction { NORTH, SOUTH, EAST, WEST }
enum class HttpStatus(val code: Int) { OK(200), NOT_FOUND(404), ERROR(500) }
enum class DayOfWeek { MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY }
```

**Use `sealed class` when:**
- Complex states with different structures
- Each state has different parameters
- Need type-safe state machine
- Modeling discriminated unions

```kotlin
// Network result with different data per state
sealed class NetworkResult<out T> {
    data class Success<T>(val data: T, val cached: Boolean) : NetworkResult<T>()
    data class Error(val message: String, val retryable: Boolean) : NetworkResult<Nothing>()
    object Loading : NetworkResult<Nothing>()
}

// UI state with different properties
sealed class UiState {
    object Idle : UiState()
    object Loading : UiState()
    data class Success(val items: List<Item>, val hasMore: Boolean) : UiState()
    data class Error(val error: Throwable, val canRetry: Boolean) : UiState()
}
```

### Can Combine Both

```kotlin
// Enum for simple status
enum class Status { PENDING, COMPLETED, FAILED }

// Sealed class for complex result with enum
sealed class TaskResult {
    data class Success(val value: String, val status: Status) : TaskResult()
    data class Failure(val error: String, val status: Status) : TaskResult()
}
```

---

## Ответ (RU)

### Ключевые Отличия

| Характеристика | Enum Class | Sealed Class |
|---------------|-----------|--------------|
| **Структура** | Фиксированный набор однородных объектов | Ограниченная иерархия классов |
| **Количество экземпляров** | Фиксировано на этапе компиляции | Можно создавать множество экземпляров |
| **Свойства** | Все экземпляры имеют одинаковую структуру | Подклассы могут иметь разные свойства |
| **Наследование** | Не может иметь подклассов | Может иметь множество подклассов |
| **Применение** | Простые фиксированные значения | Сложные состояния с разными данными |

### Enum Class

**Фиксированный набор однородных объектов с идентичной структурой:**

```kotlin
enum class Color(val rgb: Int) {
    RED(0xFF0000),
    GREEN(0x00FF00),
    BLUE(0x0000FF);

    fun hex() = "#${rgb.toString(16)}"
}

// Использование
val color = Color.RED
println(color.rgb)  // 16711680
println(color.hex()) // #ff0000

// Все enum-экземпляры имеют одинаковую структуру
when (color) {
    Color.RED -> println("Red")
    Color.GREEN -> println("Green")
    Color.BLUE -> println("Blue")
    // Исчерпывающе: компилятор знает все значения
}
```

**Характеристики:**
- Каждое значение — это единственный экземпляр
- Все значения имеют одинаковые свойства
- Нельзя создать новые экземпляры в runtime
- Можно перебрать все значения: `Color.values()`

### Sealed Class

**Ограниченная иерархия, где подклассы могут иметь разную структуру:**

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T, val timestamp: Long) : Result<T>()
    data class Error(val exception: Exception, val code: Int) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Использование - разные свойства для каждого подкласса
val result: Result<User> = Result.Success(user, System.currentTimeMillis())

when (result) {
    is Result.Success -> println("Данные: ${result.data}, время: ${result.timestamp}")
    is Result.Error -> println("Ошибка: ${result.exception.message}, код: ${result.code}")
    is Result.Loading -> println("Загрузка...")
    // Исчерпывающе: компилятор знает все подклассы
}

// Можно создать несколько экземпляров Success с разными данными
val result1 = Result.Success("data1", 123L)
val result2 = Result.Success("data2", 456L)
```

**Характеристики:**
- Допускается множество экземпляров каждого подкласса
- Подклассы могут иметь совершенно разные свойства
- Могут быть data-классы, object'ы, обычные классы в качестве подклассов
- Нельзя создать экземпляр самого sealed-класса

### Когда Использовать Каждый

**Используйте `enum class` когда:**
- Фиксированный набор значений, который не изменится
- Все значения имеют одинаковую структуру
- Простые состояния или константы
- Нужно перебрать все значения

```kotlin
enum class Direction { NORTH, SOUTH, EAST, WEST }
enum class HttpStatus(val code: Int) { OK(200), NOT_FOUND(404), ERROR(500) }
enum class DayOfWeek { MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY }
```

**Используйте `sealed class` когда:**
- Сложные состояния с разной структурой
- Каждое состояние имеет разные параметры
- Нужна типобезопасная конечная автоматизация
- Моделирование дискриминированных объединений

```kotlin
// Результат сети с разными данными для каждого состояния
sealed class NetworkResult<out T> {
    data class Success<T>(val data: T, val cached: Boolean) : NetworkResult<T>()
    data class Error(val message: String, val retryable: Boolean) : NetworkResult<Nothing>()
    object Loading : NetworkResult<Nothing>()
}

// Состояние UI с разными свойствами
sealed class UiState {
    object Idle : UiState()
    object Loading : UiState()
    data class Success(val items: List<Item>, val hasMore: Boolean) : UiState()
    data class Error(val error: Throwable, val canRetry: Boolean) : UiState()
}
```

### Можно Комбинировать Оба Подхода

```kotlin
// Enum для простого статуса
enum class Status { PENDING, COMPLETED, FAILED }

// Sealed class для сложного результата с enum
sealed class TaskResult {
    data class Success(val value: String, val status: Status) : TaskResult()
    data class Failure(val error: String, val status: Status) : TaskResult()
}
```

## Related Questions

- [[q-what-is-garbage-in-gc--programming-languages--easy]]
- [[q-suspend-function-suspension-mechanism--programming-languages--hard]]
- [[q-primitive-vs-reference-types--programming-languages--easy]]

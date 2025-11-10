---
id: lang-043
title: "Sealed Vs Enum Classes / Sealed против Enum Классов"
aliases: [Sealed Vs Enum Classes, Sealed против Enum Классов]
topic: kotlin
subtopics: [enum, oop, class-hierarchy]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-sealed-classes, q-primitive-vs-reference-types--programming-languages--easy]
created: 2025-10-15
updated: 2025-11-09
tags: [comparison, difficulty/medium, enum, kotlin, oop, programming-languages, sealed-class]
---
# Вопрос (RU)
> Каковы отличия sealed и enum классов в Kotlin?

# Question (EN)
> What are the differences between sealed and enum classes in Kotlin?

## Ответ (RU)

### Ключевые Отличия

| Характеристика | Enum Class | Sealed Class |
|---------------|-----------|--------------|
| **Структура** | Фиксированный набор именованных значений с общей объявленной структурой (возможны переопределения по константам) | Ограниченная иерархия классов |
| **Количество экземпляров** | Фиксировано на этапе компиляции для каждого значения (одиночные экземпляры констант) | Можно создавать множество экземпляров подклассов |
| **Свойства** | Все значения разделяют общий набор объявленных свойств и методов | Подклассы могут иметь разные свойства |
| **Наследование** | Наследует `Enum` и не может быть произвольно расширен, константы могут иметь собственные реализации | Может иметь несколько подклассов в пределах разрешённой области (файл/пакет/модуль) |
| **Применение** | Простые фиксированные значения или состояния | Сложные состояния с разными данными |

### Enum Class

**Фиксированный набор однородных именованных значений с общей структурой:**

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

// Все enum-константы имеют общий набор свойств/методов,
// возможны разные реализации поведения для конкретных констант
when (color) {
    Color.RED -> println("Red")
    Color.GREEN -> println("Green")
    Color.BLUE -> println("Blue")
    // Исчерпывающе: компилятор знает все значения
}
```

**Характеристики:**
- Каждое значение — это единственный экземпляр (singleton)
- Все значения разделяют общий набор объявленных свойств и методов
- Можно определить дополнительные свойства/методы и переопределять поведение на уровне конкретных констант
- Нельзя создавать новые значения enum в runtime
- Можно перебрать все значения: `Color.values()`

### Sealed Class

**Ограниченная иерархия, где подклассы могут иметь разную структуру:**

```kotlin
sealed class Result<out T> {
    data class Success<out T>(val data: T, val timestamp: Long) : Result<T>()
    data class Error(val exception: Exception, val code: Int) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Использование - разные свойства для каждого подкласса
val result: Result<User> = Result.Success(user, System.currentTimeMillis())

when (result) {
    is Result.Success -> println("Данные: ${result.data}, время: ${result.timestamp}")
    is Result.Error -> println("Ошибка: ${result.exception.message}, код: ${result.code}")
    is Result.Loading -> println("Загрузка...")
    // Исчерпывающе: компилятор знает все разрешённые подклассы
}

// Можно создать несколько экземпляров Success с разными данными
val result1 = Result.Success("data1", 123L)
val result2 = Result.Success("data2", 456L)
```

**Характеристики:**
- Допускается множество экземпляров каждого подкласса
- Подклассы могут иметь совершенно разные свойства и типы
- В качестве подклассов могут быть data-классы, object'ы, обычные классы
- Нельзя создать экземпляр самого sealed-класса
- Наследование ограничено: разрешённые подклассы должны находиться в том же файле (для ранних версий) или в том же пакете/модуле в зависимости от платформы и версии Kotlin

### Когда Использовать Каждый

**Используйте `enum class`, когда:**
- Фиксированный набор значений
- Все значения разделяют общий набор свойств и конструкторов
- Простые состояния или константы
- Нужно перебрать все значения

```kotlin
enum class Direction { NORTH, SOUTH, EAST, WEST }
enum class HttpStatus(val code: Int) { OK(200), NOT_FOUND(404), ERROR(500) }
enum class DayOfWeek { MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY }
```

**Используйте `sealed class`, когда:**
- Сложные состояния с разной структурой
- Каждое состояние имеет разные параметры
- Нужен типобезопасный конечный автомат или моделирование протокола
- Нужно моделировать дискриминированные объединения

```kotlin
// Результат сети с разными данными для каждого состояния
sealed class NetworkResult<out T> {
    data class Success<out T>(val data: T, val cached: Boolean) : NetworkResult<T>()
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

## Answer (EN)

### Key Differences

| Feature | Enum Class | Sealed Class |
|---------|-----------|--------------|
| **Structure** | Fixed set of named values with a shared declared structure (per-constant overrides possible) | Restricted class hierarchy |
| **Instance count** | One singleton instance per enum constant, fixed at compile time | Can create multiple instances of subclasses |
| **Properties** | All values share the same declared properties/methods | Subclasses can have different properties |
| **Inheritance** | Extends `Enum` and cannot be arbitrarily subclassed; constants may provide their own implementations | Can have multiple subclasses within the allowed scope (file/package/module) |
| **Use case** | Simple fixed values or states | Complex states with different data |

### Enum Class

**Fixed set of homogeneous named values with a common structure:**

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

// All enum constants share the same declared properties/methods;
// per-constant behavior overrides are possible
when (color) {
    Color.RED -> println("Red")
    Color.GREEN -> println("Green")
    Color.BLUE -> println("Blue")
    // Exhaustive: compiler knows all values
}
```

**Characteristics:**
- Each enum constant is a single (singleton) instance
- All values share the same declared properties and methods
- You can define additional properties/methods and override behavior per constant
- Cannot create new enum constants at runtime
- Can iterate over all values: `Color.values()`

### Sealed Class

**Restricted hierarchy where subclasses can have different structures:**

```kotlin
sealed class Result<out T> {
    data class Success<out T>(val data: T, val timestamp: Long) : Result<T>()
    data class Error(val exception: Exception, val code: Int) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Usage - different properties per subclass
val result: Result<User> = Result.Success(user, System.currentTimeMillis())

when (result) {
    is Result.Success -> println("Data: ${result.data}, time: ${result.timestamp}")
    is Result.Error -> println("Error: ${result.exception.message}, code: ${result.code}")
    is Result.Loading -> println("Loading...")
    // Exhaustive: compiler knows all permitted subclasses
}

// Can create multiple Success instances with different data
val result1 = Result.Success("data1", 123L)
val result2 = Result.Success("data2", 456L)
```

**Characteristics:**
- Multiple instances of each subclass allowed
- Subclasses can have completely different properties and types
- Subclasses can be data classes, objects, or regular classes
- Cannot create instances of sealed class itself
- Inheritance is restricted: permitted subclasses must be defined in the same file (older versions) or in the same package/module depending on platform and Kotlin version

### When to Use Each

**Use `enum class` when:**
- Fixed set of values
- All values share the same declared properties/constructors
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
- Need a type-safe state machine or protocol modeling
- Modeling discriminated unions

```kotlin
// Network result with different data per state
sealed class NetworkResult<out T> {
    data class Success<out T>(val data: T, val cached: Boolean) : NetworkResult<T>()
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

## Дополнительные вопросы (RU)

- В чем ключевые отличия от Java-подхода?
- Когда вы бы применили это на практике?
- Каковы распространенные ошибки, которых следует избегать?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-sealed-classes]]

## Связанные вопросы (RU)

- [[q-what-is-garbage-in-gc--programming-languages--easy]]
- [[q-suspend-function-suspension-mechanism--programming-languages--hard]]
- [[q-primitive-vs-reference-types--programming-languages--easy]]

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-sealed-classes]]

## Related Questions

- [[q-what-is-garbage-in-gc--programming-languages--easy]]
- [[q-suspend-function-suspension-mechanism--programming-languages--hard]]
- [[q-primitive-vs-reference-types--programming-languages--easy]]
